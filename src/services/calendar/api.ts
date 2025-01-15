import { CALENDAR_CONFIG } from '../../config/calendar';
import * as jose from 'jose';

const BASE_URL = 'https://www.googleapis.com/calendar/v3';

interface CalendarEvent {
  id?: string;
  summary?: string;
  description?: string;
  start: { dateTime?: string; date?: string };
  end: { dateTime?: string; date?: string };
  location?: string;
}

// Token management
let cachedToken: string | null = null;
let tokenExpiration: number | null = null;
const TOKEN_EXPIRY_BUFFER = 5 * 60 * 1000; // 5 minutes buffer

/**
 * Generates a JWT token for service account authentication
 */
async function generateJWT(): Promise<string> {
  const privateKeyStr = import.meta.env.VITE_GOOGLE_PRIVATE_KEY;
  const clientEmail = import.meta.env.VITE_GOOGLE_CLIENT_EMAIL;

  if (!privateKeyStr || !clientEmail) {
    console.error('Missing Google service account credentials:', {
      privateKeyPresent: !!privateKeyStr,
      clientEmailPresent: !!clientEmail
    });
    throw new Error('Google service account credentials are missing');
  }

  // Properly decode the private key (replace escaped newlines)
  const privateKey = privateKeyStr.replace(/\\n/g, '\n')
    // Ensure the key starts and ends with the correct markers
    .replace(/^[^-]*/, '-----BEGIN PRIVATE KEY-----\n')
    .replace(/[^-]*$/, '\n-----END PRIVATE KEY-----');

  try {
    // Use jose library for JWT signing
    const alg = 'RS256';
    const now = Math.floor(Date.now() / 1000);

    const jwt = await new jose.SignJWT({
      iss: clientEmail,
      sub: clientEmail,
      aud: 'https://oauth2.googleapis.com/token',
      iat: now,
      exp: now + 3600, // Token valid for 1 hour
      scope: 'https://www.googleapis.com/auth/calendar'
    })
    .setProtectedHeader({ alg })
    .sign(await jose.importPKCS8(privateKey, alg));

    return jwt;
  } catch (error) {
    console.error('JWT generation error:', error, 'Private Key:', privateKey);
    throw new Error('Failed to generate JWT');
  }
}

/**
 * Gets an access token using JWT
 */
async function getAccessToken(): Promise<string> {
  try {
    // Return cached token if still valid
    if (cachedToken && tokenExpiration && Date.now() < tokenExpiration - TOKEN_EXPIRY_BUFFER) {
      return cachedToken;
    }

    const assertion = await generateJWT();

    const response = await fetch('https://oauth2.googleapis.com/token', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({
        grant_type: 'urn:ietf:params:oauth:grant-type:jwt-bearer',
        assertion: assertion,
      }),
    });

    if (!response.ok) {
      const errorData = await response.text();
      console.error('Token request error:', {
        status: response.status,
        body: errorData
      });
      throw new Error(`Failed to obtain access token: ${errorData}`);
    }

    const tokenData = await response.json();

    // Cache token
    cachedToken = tokenData.access_token;
    tokenExpiration = Date.now() + (tokenData.expires_in || 3600) * 1000;

    return tokenData.access_token;
  } catch (error) {
    console.error('Error getting access token:', error);
    throw new Error('Failed to authenticate with Google Calendar');
  }
}

/**
 * Fetches calendar events from Google Calendar API for a given time range.
 * @param timeMin - The start of the time range in ISO format.
 * @param timeMax - The end of the time range in ISO format.
 * @returns A promise that resolves to an array of calendar events.
 */
export async function fetchCalendarEvents(timeMin: string, timeMax: string): Promise<CalendarEvent[]> {
  try {
    const accessToken = await getAccessToken();

    const params = new URLSearchParams({
      timeMin,
      timeMax,
      singleEvents: 'true',
      orderBy: 'startTime',
    });

    const url = `${BASE_URL}/calendars/${encodeURIComponent(CALENDAR_CONFIG.calendarId)}/events?${params}`;

    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`,
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      console.error('Calendar API error:', {
        status: response.status,
        data: errorData,
        calendarId: CALENDAR_CONFIG.calendarId
      });
      throw new Error(`Failed to fetch calendar events: ${JSON.stringify(errorData)}`);
    }

    const data = await response.json();
    return Array.isArray(data.items) ? data.items : [];
  } catch (error) {
    console.error('Error fetching calendar events:', error);
    throw error;
  }
}

/**
 * Creates a new calendar event
 */
export async function createCalendarEvent(event: CalendarEvent): Promise<CalendarEvent> {
  try {
    const accessToken = await getAccessToken();

    console.log('Attempting to create event with:', JSON.stringify(event, null, 2));

    const response = await fetch(
      `${BASE_URL}/calendars/${encodeURIComponent(CALENDAR_CONFIG.calendarId)}/events`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`,
        },
        body: JSON.stringify({
          summary: event.summary || '',
          description: event.description || '',
          start: {
            dateTime: event.start.dateTime || event.start.date,
            timeZone: 'Europe/Moscow'
          },
          end: {
            dateTime: event.end.dateTime || event.end.date,
            timeZone: 'Europe/Moscow'
          },
          location: event.location || ''
        }),
      }
    );

    const responseBody = await response.text();
    console.log('Response status:', response.status);
    console.log('Response body:', responseBody);

    if (!response.ok) {
      console.error('Detailed error:', {
        status: response.status,
        body: responseBody,
        event
      });
      throw new Error(`Failed to create calendar event: ${responseBody}`);
    }

    const parsedResponse = JSON.parse(responseBody);
    return {
      id: parsedResponse.id,
      summary: parsedResponse.summary,
      description: parsedResponse.description,
      start: parsedResponse.start,
      end: parsedResponse.end,
      location: parsedResponse.location
    };
  } catch (error) {
    console.error('Error creating calendar event:', error);
    throw error;
  }
}