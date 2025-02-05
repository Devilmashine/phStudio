interface TermsCheckboxesProps {
  termsAccepted: boolean;
  privacyAccepted: boolean;
  onTermsChange: () => void;
  onPrivacyChange: () => void;
  onShowTerms: () => void;
  onShowPrivacy: () => void;
} 