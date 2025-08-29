export interface TermsCheckboxesProps {
  termsContent: string;
  privacyContent: string;
  termsAccepted: boolean;
  privacyAccepted: boolean;
  onTermsAcceptChange: (value: boolean) => void;
  onPrivacyAcceptChange: (value: boolean) => void;
  onShowTermsModal: () => void;
  onShowPrivacyModal: () => void;
}
