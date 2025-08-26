import React, { createContext, useContext, useReducer, useCallback, useEffect } from 'react';
import { createBooking } from '../services/booking';
import { studio } from '../data/studio';

// Types
interface BookingState {
  selectedDate: Date | null;
  selectedTimes: string[];
  clientInfo: {
    name: string;
    phone: string;
    email?: string;
  };
  agreementState: {
    termsAccepted: boolean;
    privacyAccepted: boolean;
    studioRulesAccepted: boolean;
  };
  uiState: {
    isSubmitting: boolean;
    formErrors: string[];
    showTermsModal: boolean;
    showPrivacyModal: boolean;
    showStudioRulesModal: boolean;
  };
  bookingOptions: {
    peopleCount: number;
    totalPrice: number;
  };
  cache: {
    availableSlots: Record<string, string[]>;
    lastFetched: Record<string, number>;
  };
}

type BookingAction =
  | { type: 'SET_DATE'; payload: Date | null }
  | { type: 'SET_TIMES'; payload: string[] }
  | { type: 'TOGGLE_TIME'; payload: string }
  | { type: 'SET_CLIENT_INFO'; payload: Partial<BookingState['clientInfo']> }
  | { type: 'SET_AGREEMENT'; payload: Partial<BookingState['agreementState']> }
  | { type: 'SET_UI_STATE'; payload: Partial<BookingState['uiState']> }
  | { type: 'SET_BOOKING_OPTIONS'; payload: Partial<BookingState['bookingOptions']> }
  | { type: 'SET_CACHE'; payload: { date: string; slots: string[] } }
  | { type: 'RESET_FORM' }
  | { type: 'SET_FORM_ERRORS'; payload: string[] };

const initialState: BookingState = {
  selectedDate: null,
  selectedTimes: [],
  clientInfo: {
    name: '',
    phone: '',
    email: '',
  },
  agreementState: {
    termsAccepted: false,
    privacyAccepted: false,
    studioRulesAccepted: false,
  },
  uiState: {
    isSubmitting: false,
    formErrors: [],
    showTermsModal: false,
    showPrivacyModal: false,
    showStudioRulesModal: false,
  },
  bookingOptions: {
    peopleCount: 1,
    totalPrice: 0,
  },
  cache: {
    availableSlots: {},
    lastFetched: {},
  },
};

function bookingReducer(state: BookingState, action: BookingAction): BookingState {
  switch (action.type) {
    case 'SET_DATE':
      return {
        ...state,
        selectedDate: action.payload,
        selectedTimes: [], // Reset times when date changes
      };

    case 'SET_TIMES':
      return {
        ...state,
        selectedTimes: action.payload,
      };

    case 'TOGGLE_TIME':
      const timeToToggle = action.payload;
      const currentTimes = state.selectedTimes;
      const newTimes = currentTimes.includes(timeToToggle)
        ? currentTimes.filter(t => t !== timeToToggle)
        : [...currentTimes, timeToToggle].sort();
      
      return {
        ...state,
        selectedTimes: newTimes,
      };

    case 'SET_CLIENT_INFO':
      return {
        ...state,
        clientInfo: { ...state.clientInfo, ...action.payload },
      };

    case 'SET_AGREEMENT':
      return {
        ...state,
        agreementState: { ...state.agreementState, ...action.payload },
      };

    case 'SET_UI_STATE':
      return {
        ...state,
        uiState: { ...state.uiState, ...action.payload },
      };

    case 'SET_BOOKING_OPTIONS':
      return {
        ...state,
        bookingOptions: { ...state.bookingOptions, ...action.payload },
      };

    case 'SET_CACHE':
      return {
        ...state,
        cache: {
          availableSlots: {
            ...state.cache.availableSlots,
            [action.payload.date]: action.payload.slots,
          },
          lastFetched: {
            ...state.cache.lastFetched,
            [action.payload.date]: Date.now(),
          },
        },
      };

    case 'RESET_FORM':
      return initialState;

    case 'SET_FORM_ERRORS':
      return {
        ...state,
        uiState: { ...state.uiState, formErrors: action.payload },
      };

    default:
      return state;
  }
}

// Context
interface BookingContextType {
  state: BookingState;
  actions: {
    setDate: (date: Date | null) => void;
    toggleTime: (time: string) => void;
    setClientInfo: (info: Partial<BookingState['clientInfo']>) => void;
    setAgreement: (agreement: Partial<BookingState['agreementState']>) => void;
    setUIState: (uiState: Partial<BookingState['uiState']>) => void;
    setPeopleCount: (count: number) => void;
    submitBooking: () => Promise<boolean>;
    resetForm: () => void;
    getAvailableSlots: (date: Date) => Promise<string[]>;
    validateForm: () => string[];
  };
}

const BookingContext = createContext<BookingContextType | undefined>(undefined);

// Provider
export const BookingProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(bookingReducer, initialState);

  // Calculate total price whenever relevant state changes
  useEffect(() => {
    const basePeople = 5;
    const extraPeople = Math.max(0, state.bookingOptions.peopleCount - basePeople);
    const extraFee = extraPeople * 200 * state.selectedTimes.length;
    const totalPrice = state.selectedTimes.length * studio.pricePerHour + extraFee;

    if (totalPrice !== state.bookingOptions.totalPrice) {
      dispatch({
        type: 'SET_BOOKING_OPTIONS',
        payload: { totalPrice },
      });
    }
  }, [state.selectedTimes.length, state.bookingOptions.peopleCount, state.bookingOptions.totalPrice]);

  // Actions
  const actions = {
    setDate: useCallback((date: Date | null) => {
      dispatch({ type: 'SET_DATE', payload: date });
    }, []),

    toggleTime: useCallback((time: string) => {
      dispatch({ type: 'TOGGLE_TIME', payload: time });
    }, []),

    setClientInfo: useCallback((info: Partial<BookingState['clientInfo']>) => {
      dispatch({ type: 'SET_CLIENT_INFO', payload: info });
    }, []),

    setAgreement: useCallback((agreement: Partial<BookingState['agreementState']>) => {
      dispatch({ type: 'SET_AGREEMENT', payload: agreement });
    }, []),

    setUIState: useCallback((uiState: Partial<BookingState['uiState']>) => {
      dispatch({ type: 'SET_UI_STATE', payload: uiState });
    }, []),

    setPeopleCount: useCallback((count: number) => {
      dispatch({ 
        type: 'SET_BOOKING_OPTIONS', 
        payload: { peopleCount: Math.max(1, Math.min(30, count)) } 
      });
    }, []),

    getAvailableSlots: useCallback(async (date: Date): Promise<string[]> => {
      const dateKey = date.toISOString().split('T')[0];
      const now = Date.now();
      const cacheExpiry = 5 * 60 * 1000; // 5 minutes

      // Check cache first
      const cached = state.cache.availableSlots[dateKey];
      const lastFetched = state.cache.lastFetched[dateKey];

      if (cached && lastFetched && (now - lastFetched) < cacheExpiry) {
        return cached;
      }

      try {
        // Use real API to fetch day availability
        const { fetchDayDetails } = await import('../services/calendar/api');
        const dayDetails = await fetchDayDetails(dateKey);
        
        // Extract available time slots from API response
        const availableSlots = dayDetails.slots
          .filter(slot => slot.available)
          .map(slot => slot.time);
        
        // Cache the result
        dispatch({ 
          type: 'SET_CACHE', 
          payload: { date: dateKey, slots: availableSlots } 
        });

        return availableSlots;
      } catch (error) {
        console.error('Error fetching available slots from API:', error);
        // Return empty array instead of hardcoded data
        return [];
      }
    }, [state.cache]),

    validateForm: useCallback((): string[] => {
      const errors: string[] = [];

      if (!state.selectedDate) {
        errors.push('Выберите дату');
      }

      if (state.selectedTimes.length === 0) {
        errors.push('Выберите время');
      }

      if (!state.clientInfo.name || state.clientInfo.name.trim().length < 2) {
        errors.push('Введите корректное имя (минимум 2 символа)');
      }

      const phoneRegex = /^(\+7|7|8)?[\s-]?\(?[489][0-9]{2}\)?[\s-]?[0-9]{3}[\s-]?[0-9]{2}[\s-]?[0-9]{2}$/;
      if (!state.clientInfo.phone || !phoneRegex.test(state.clientInfo.phone.replace(/\D/g, ''))) {
        errors.push('Введите корректный номер телефона');
      }

      if (!state.agreementState.termsAccepted) {
        errors.push('Необходимо принять условия публичной оферты');
      }

      if (!state.agreementState.privacyAccepted) {
        errors.push('Необходимо дать согласие на обработку персональных данных');
      }

      if (!state.agreementState.studioRulesAccepted) {
        errors.push('Необходимо ознакомиться с правилами студии');
      }

      if (state.bookingOptions.peopleCount < 1) {
        errors.push('Количество человек должно быть больше 0');
      }

      if (state.bookingOptions.peopleCount > 30) {
        errors.push('Максимальное количество человек - 30');
      }

      dispatch({ type: 'SET_FORM_ERRORS', payload: errors });
      return errors;
    }, [state]),

    submitBooking: useCallback(async (): Promise<boolean> => {
      const errors = actions.validateForm();
      
      if (errors.length > 0) {
        return false;
      }

      dispatch({ type: 'SET_UI_STATE', payload: { isSubmitting: true } });

      try {
        const bookingData = {
          date: state.selectedDate!.toISOString().split('T')[0],
          times: state.selectedTimes,
          name: state.clientInfo.name,
          phone: state.clientInfo.phone,
          totalPrice: state.bookingOptions.totalPrice,
        };

        const result = await createBooking(bookingData);
        
        if (result && result.id) {
          dispatch({ type: 'RESET_FORM' });
          return true;
        } else {
          dispatch({ 
            type: 'SET_FORM_ERRORS', 
            payload: ['Ошибка при создании бронирования'] 
          });
          return false;
        }
      } catch (error) {
        console.error('Booking submission error:', error);
        dispatch({ 
          type: 'SET_FORM_ERRORS', 
          payload: ['Произошла ошибка при отправке. Попробуйте еще раз.'] 
        });
        return false;
      } finally {
        dispatch({ type: 'SET_UI_STATE', payload: { isSubmitting: false } });
      }
    }, [state]),

    resetForm: useCallback(() => {
      dispatch({ type: 'RESET_FORM' });
    }, []),
  };

  const contextValue: BookingContextType = {
    state,
    actions,
  };

  return (
    <BookingContext.Provider value={contextValue}>
      {children}
    </BookingContext.Provider>
  );
};

// Hook
export const useBooking = () => {
  const context = useContext(BookingContext);
  if (context === undefined) {
    throw new Error('useBooking must be used within a BookingProvider');
  }
  return context;
};

// Selectors for optimized re-renders
export const useBookingSelectors = () => {
  const { state } = useBooking();
  
  return {
    selectedDate: state.selectedDate,
    selectedTimes: state.selectedTimes,
    clientInfo: state.clientInfo,
    agreementState: state.agreementState,
    uiState: state.uiState,
    bookingOptions: state.bookingOptions,
    totalPrice: state.bookingOptions.totalPrice,
    isSubmitting: state.uiState.isSubmitting,
    formErrors: state.uiState.formErrors,
  };
};