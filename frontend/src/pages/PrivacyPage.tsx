import './PrivacyPage.css';

export default function PrivacyPage() {
  return (
    <div className="privacy-page">
      <div className="privacy-content">
        <h1>Privacy Policy</h1>
        <p className="last-updated">Last Updated: February 9, 2026</p>

        <section>
          <h2>Overview</h2>
          <p>
            Solmu - Guitar Music Network ("we", "our", or "us") is committed to protecting your privacy. 
            This Privacy Policy explains how we collect, use, and safeguard your information when you use our service.
          </p>
        </section>

        <section>
          <h2>Information We Collect</h2>
          <h3>User-Provided Information</h3>
          <ul>
            <li><strong>Suggestions:</strong> When you submit suggestions for composer or work corrections, we collect the information you provide in the suggestion form and any comments you include.</li>
            <li><strong>Admin Accounts:</strong> If you have admin access, we store your username and email address for authentication purposes.</li>
          </ul>
          
          <h3>Automatically Collected Information</h3>
          <ul>
            <li><strong>Usage Data:</strong> We may collect information about how you interact with our service, including pages viewed and search queries performed.</li>
            <li><strong>Session Data:</strong> We use session cookies to maintain your login state if you are an administrator.</li>
          </ul>
        </section>

        <section>
          <h2>How We Use Your Information</h2>
          <p>We use the collected information for the following purposes:</p>
          <ul>
            <li>To process and review user suggestions for improving our database</li>
            <li>To provide and maintain our service</li>
            <li>To authenticate and authorize admin users</li>
            <li>To improve and optimize our website functionality</li>
            <li>To communicate with users regarding their submissions</li>
          </ul>
        </section>

        <section>
          <h2>Data Storage and Security</h2>
          <p>
            Your data is stored securely on our servers. We implement appropriate technical and organizational 
            measures to protect your personal information against unauthorized access, alteration, disclosure, or destruction.
          </p>
          <p>
            User suggestions are sent via email to our administrators and are not stored in a publicly accessible database.
          </p>
        </section>

        <section>
          <h2>Cookies</h2>
          <p>
            We use session cookies to maintain authentication for admin users. These cookies are essential for 
            the functionality of the admin portal and are deleted when you close your browser or log out.
          </p>
        </section>

        <section>
          <h2>Third-Party Services</h2>
          <p>
            Our service is hosted on Amazon Web Services (AWS). We do not share your personal information 
            with third parties except as necessary to provide our service (e.g., hosting providers) or as required by law.
          </p>
        </section>

        <section>
          <h2>External Links</h2>
          <p>
            Our service contains links to external websites (IMSLP, YouTube, etc.). We are not responsible 
            for the privacy practices of these external sites. We encourage you to review their privacy policies.
          </p>
        </section>

        <section>
          <h2>Your Rights</h2>
          <p>You have the right to:</p>
          <ul>
            <li>Request access to your personal information</li>
            <li>Request correction or deletion of your personal information</li>
            <li>Withdraw consent for data processing (where applicable)</li>
            <li>Object to certain types of data processing</li>
          </ul>
          <p>
            To exercise these rights or for any privacy-related questions, please contact us at: <strong>jeswashburn@gmail.com</strong>
          </p>
        </section>

        <section>
          <h2>Children's Privacy</h2>
          <p>
            Our service is not directed to children under the age of 13. We do not knowingly collect 
            personal information from children under 13.
          </p>
        </section>

        <section>
          <h2>Changes to This Privacy Policy</h2>
          <p>
            We may update this Privacy Policy from time to time. We will notify users of any material 
            changes by updating the "Last Updated" date at the top of this policy. Your continued use 
            of the service after such changes constitutes acceptance of the updated policy.
          </p>
        </section>

        <section>
          <h2>Contact Us</h2>
          <p>
            If you have questions or concerns about this Privacy Policy, please contact us at:
          </p>
          <p className="contact-info">
            <strong>Email:</strong> jeswashburn@gmail.com
          </p>
        </section>
      </div>
    </div>
  );
}
