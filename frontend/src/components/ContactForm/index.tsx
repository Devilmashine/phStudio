export interface ContactFormProps {
  name: string;
  phone: string;
  comment: string;
  onNameChange: (value: string) => void;
  onPhoneChange: (value: string) => void;
  onCommentChange: (value: string) => void;
}
