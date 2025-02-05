import React from 'react';

export interface ContactFormProps {
  name: string;
  onNameChange: (value: string) => void;
  phone: string;
  onPhoneChange: (value: string) => void;
  comment: string;
  onCommentChange: (value: string) => void;
  errors?: { [key: string]: string };
}

const ContactForm: React.FC<ContactFormProps> = ({
  name,
  onNameChange,
  phone,
  onPhoneChange,
  comment,
  onCommentChange,
  errors
}) => {
  // ... component implementation ...
};

export default ContactForm; 