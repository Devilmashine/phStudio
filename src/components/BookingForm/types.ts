export interface BookingFormData {
  selectedDate: Date | null;
  selectedTimes: string[];
  name: string;
  phone: string;
  termsAccepted: boolean;
  privacyAccepted: boolean;
}

export interface BookingFormProps {
  onSubmit: (data: BookingFormData) => void;
}