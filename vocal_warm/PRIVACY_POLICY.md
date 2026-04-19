# Privacy Policy for VocalWarm

**Last Updated: April 15, 2026**

[한국어](PRIVACY_POLICY_ko) | [日本語](PRIVACY_POLICY_ja) | [中文](PRIVACY_POLICY_zh)

VocalWarm is operated by **TtomStudio** ("we," "our," or "us") and is committed to protecting your privacy. This Privacy Policy explains how we collect, use, and safeguard your information when you use our mobile application.

## 1. Information We Collect

### A. Audio Data (Microphone)
To provide vocal range testing and pitch detection features, VocalWarm requires access to your device's microphone.
- **Local Processing**: All audio analysis is performed **locally on your device**.
- **No Recording/Storage**: We do not record, store, or transmit your voice or any audio data to our servers.

### B. Personal Information
If you choose to create an account, we collect:
- **Email Address**: Used for authentication and account recovery via Firebase Authentication.
- **Display Name**: To personalize your experience.

### C. Practice Records (Cloud Backup)
When cloud backup is enabled (default ON), the following practice records are stored in Google Cloud Firestore, scoped to your user ID:
- **Practice Sessions**: date, duration in minutes, exercise count, and creation timestamp.
- **Vocal Range Results**: tested date, lowest/highest detected notes, octave range, note count, and detected vocal type (e.g., soprano/tenor).
- **Note Accuracies**: per-note accuracy percentages from each vocal range test.

These records are used to restore your history when you reinstall the app or change devices. No raw audio is included. You can disable cloud backup at any time via **Settings > Cloud Backup**.

### D. Usage Data
We use Firebase Analytics to collect anonymous technical information, such as:
- Device type and OS version.
- App crashes and performance metrics.
- Frequency of feature usage (e.g., how many warm-ups completed).

## 2. How We Use Your Information
- To provide and maintain our Service.
- To personalize your vocal training experience.
- To back up and restore your practice records across devices.
- To improve our application based on anonymous usage patterns.
- To communicate with you regarding your account.

## 3. Data Sharing
We do **not** sell or share your personal data with third parties for marketing purposes. We use the following third-party services:
- **Google Firebase Authentication**: For account sign-in.
- **Google Cloud Firestore**: For practice-record backup (only while cloud backup is enabled).
- **Google Firebase Analytics**: For anonymous app usage metrics.

## 4. Your Rights
You can delete your account and all associated data (Firebase Auth identity, Firestore-stored practice records, and local device records) at any time through **Settings > Delete Account & Data**. You may also withdraw microphone permission at any time via your device settings.

## 5. Data Retention
Practice records stored via cloud backup are retained until you delete your account or disable cloud backup and delete them locally. When you delete your account, all records under your user ID in Firestore are removed via a client-side cascading delete, and your Firebase Authentication user is deleted.

## 6. Contact Us
If you have any questions about this Privacy Policy, please contact us at:
**official@ttomstudio.com**
