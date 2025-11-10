---
name: data-protection
description: Use me for data privacy and protection reviews, GDPR/CCPA compliance, encryption at rest and in transit, PII handling, data minimization, data retention policies, and sensitive data classification. I return ASVS-mapped findings with rule IDs and secure code examples.
---

# Data Protection Skill

**I provide data privacy and protection guidance following ASVS, GDPR, CCPA, and CWE standards.**

## Activation Triggers

**I respond to these queries and tasks**:
- Data privacy and protection reviews
- GDPR and CCPA compliance validation
- Encryption at rest and in transit
- PII (Personally Identifiable Information) handling
- Sensitive data classification and tagging
- Data minimization and retention policies
- Data anonymization and pseudonymization
- Right to erasure (GDPR Article 17)
- Data breach notification requirements
- Cross-border data transfer security

**Manual activation**: Use `/data-protection` or mention "data privacy review"

**Agent variant**: For parallel analysis with other security checks, use the `data-protection-specialist` agent via the Task tool

## Security Knowledge Base

### Encryption Requirements (4 rules)
- Encrypt PII and sensitive data at rest
- Use TLS 1.2+ for data in transit
- Implement field-level encryption for highly sensitive data
- Use strong encryption algorithms (AES-256, RSA-2048+)
- Protect encryption keys with KMS/HSM
- Never store encryption keys with encrypted data

### PII Handling (4 rules)
- Identify and classify PII (email, phone, SSN, health data)
- Implement purpose limitation (collect only what's needed)
- Obtain explicit consent for PII processing
- Provide data access and export capabilities
- Implement data deletion and right to erasure
- Anonymize or pseudonymize PII when possible

### Data Minimization (3 rules)
- Collect minimum data necessary for purpose
- Implement data retention policies with auto-deletion
- Avoid collecting sensitive data unless required
- Review data collection forms and APIs
- Remove unnecessary data fields
- Document data collection justification

### Privacy Controls (3 rules)
- Implement privacy by design and by default
- Provide user consent management
- Enable data export in machine-readable format
- Support data portability (GDPR Article 20)
- Implement audit logs for data access
- Notify users of data breaches within 72 hours

## Common Vulnerabilities

| Vulnerability | Severity | CWE | GDPR/Privacy |
|--------------|----------|-----|---------------|
| Unencrypted PII storage | **CRITICAL** | CWE-311 | GDPR Art. 32 |
| Missing consent mechanisms | **HIGH** | CWE-359 | GDPR Art. 6, 7 |
| No data retention policy | **HIGH** | CWE-359 | GDPR Art. 5, 17 |
| PII in logs or error messages | **HIGH** | CWE-532 | GDPR Art. 32 |
| No data deletion capability | **MEDIUM** | CWE-359 | GDPR Art. 17 |
| Unencrypted data in transit | **HIGH** | CWE-319 | GDPR Art. 32 |

## Detection Patterns

**I scan for these security issues**:

### Unencrypted PII Storage
```python
# ❌ VULNERABLE: Plaintext PII in database
class User(models.Model):
    email = models.EmailField()  # PII - not encrypted!
    phone = models.CharField(max_length=20)  # PII - not encrypted!
    ssn = models.CharField(max_length=11)  # Highly sensitive - not encrypted!
    medical_record = models.TextField()  # Highly sensitive - not encrypted!

# ❌ VULNERABLE: PII in plaintext files
with open('users.csv', 'w') as f:
    f.write(f"{user.email},{user.ssn}\n")  # Plaintext PII!

# ✅ SECURE: Encrypted PII with field-level encryption
from django_cryptography.fields import encrypt
from google.cloud import kms
import base64

class User(models.Model):
    # Standard fields (non-PII)
    username = models.CharField(max_length=150, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Encrypted PII fields
    email = encrypt(models.EmailField())
    phone = encrypt(models.CharField(max_length=20, null=True, blank=True))

    # Highly sensitive - separate encryption key
    ssn_encrypted = models.BinaryField(null=True, blank=True)
    medical_record_encrypted = models.BinaryField(null=True, blank=True)

    class Meta:
        db_table = 'users'
        indexes = [
            # Can't index encrypted fields - use hash for lookup
            models.Index(fields=['username']),
        ]

    def set_ssn(self, ssn_plaintext):
        """Encrypt SSN with KMS"""
        if not ssn_plaintext:
            self.ssn_encrypted = None
            return

        kms_client = kms.KeyManagementServiceClient()
        key_name = settings.SSN_ENCRYPTION_KEY_ID

        encrypt_response = kms_client.encrypt(
            request={'name': key_name, 'plaintext': ssn_plaintext.encode()}
        )
        self.ssn_encrypted = encrypt_response.ciphertext

    def get_ssn(self):
        """Decrypt SSN with KMS"""
        if not self.ssn_encrypted:
            return None

        kms_client = kms.KeyManagementServiceClient()
        key_name = settings.SSN_ENCRYPTION_KEY_ID

        decrypt_response = kms_client.decrypt(
            request={'name': key_name, 'ciphertext': self.ssn_encrypted}
        )
        return decrypt_response.plaintext.decode()

    # Audit log for PII access
    def log_pii_access(self, accessor_id, field_name):
        PIIAccessLog.objects.create(
            user_id=self.id,
            accessor_id=accessor_id,
            field_accessed=field_name,
            timestamp=timezone.now()
        )
```

### Data Minimization and Retention
```javascript
// ❌ VULNERABLE: Collecting unnecessary data
const userSchema = new Schema({
  email: String,
  password: String,
  phone: String,
  address: String,
  ssn: String,  // Why collecting SSN?
  mothersMaidenName: String,  // Unnecessary!
  dateOfBirth: Date,  // Do you need full DOB?
  bloodType: String,  // Unnecessary for most apps
  createdAt: { type: Date, default: Date.now }
  // No deletion timestamp!
});

// ❌ VULNERABLE: No retention policy
// Data kept indefinitely, never deleted

// ✅ SECURE: Data minimization with retention policy
const userSchema = new Schema({
  // Essential fields only
  email: {
    type: String,
    required: true,
    unique: true,
    // Hashed for lookup, encrypted for storage
    index: true
  },
  passwordHash: String,

  // Optional fields with clear purpose
  phone: {
    type: String,
    required: false,
    // Encrypted, document purpose: "2FA verification"
  },

  // Consent tracking
  consentVersion: {
    type: String,
    required: true
  },
  consentGivenAt: {
    type: Date,
    required: true
  },

  // Retention policy fields
  createdAt: {
    type: Date,
    default: Date.now,
    index: true
  },
  lastActiveAt: {
    type: Date,
    default: Date.now,
    index: true
  },
  scheduledDeletionAt: {
    type: Date,
    index: true
  },
  deletedAt: {
    type: Date,
    index: true
  }
});

// Data retention policy: Delete inactive users after 2 years
userSchema.pre('save', function(next) {
  if (this.isNew) {
    // Schedule deletion 2 years after creation
    this.scheduledDeletionAt = new Date(
      Date.now() + (2 * 365 * 24 * 60 * 60 * 1000)
    );
  }
  next();
});

// Automated retention enforcement
async function enforceRetentionPolicy() {
  const cutoffDate = new Date(Date.now() - (2 * 365 * 24 * 60 * 60 * 1000));

  // Find users inactive for 2 years
  const usersToDelete = await User.find({
    lastActiveAt: { $lt: cutoffDate },
    deletedAt: null
  });

  for (const user of usersToDelete) {
    // Soft delete (GDPR requires audit trail)
    user.deletedAt = new Date();

    // Anonymize PII
    user.email = `deleted-${user._id}@anonymized.local`;
    user.phone = null;

    await user.save();

    // Log deletion for compliance
    await ComplianceLog.create({
      action: 'data_retention_deletion',
      userId: user._id,
      reason: 'Automated retention policy (2 years inactive)',
      timestamp: new Date()
    });
  }
}

// Run daily
cron.schedule('0 2 * * *', enforceRetentionPolicy);
```

### GDPR Consent Management
```python
# ❌ VULNERABLE: No consent tracking
class User(models.Model):
    email = models.EmailField()
    # No consent fields!

# Usage: Silently collect data
user = User.objects.create(email=email)  # No consent!

# ❌ VULNERABLE: Implicit consent
def signup(request):
    # Assumes consent by signup - not GDPR compliant!
    user = User.objects.create(email=request.POST['email'])

# ✅ SECURE: Explicit consent with granular controls
from django.db import models
from django.utils import timezone

class ConsentType(models.TextChoices):
    ESSENTIAL = 'essential', 'Essential (Required)'
    ANALYTICS = 'analytics', 'Analytics'
    MARKETING = 'marketing', 'Marketing Communications'
    THIRD_PARTY = 'third_party', 'Third-Party Data Sharing'

class UserConsent(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='consents')
    consent_type = models.CharField(max_length=20, choices=ConsentType.choices)
    granted = models.BooleanField(default=False)
    granted_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    consent_text_shown = models.TextField()  # What user consented to
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()

    class Meta:
        unique_together = ['user', 'consent_type']
        indexes = [
            models.Index(fields=['user', 'consent_type', 'granted']),
        ]

class User(models.Model):
    email = encrypt(models.EmailField())
    created_at = models.DateTimeField(auto_now_add=True)

    # GDPR required capabilities
    data_processing_consent_version = models.CharField(max_length=10)
    privacy_policy_accepted_at = models.DateTimeField()

    def grant_consent(self, consent_type, request, consent_text):
        """Grant specific consent with audit trail"""
        consent, created = UserConsent.objects.get_or_create(
            user=self,
            consent_type=consent_type,
            defaults={
                'granted': True,
                'granted_at': timezone.now(),
                'consent_text_shown': consent_text,
                'ip_address': request.META.get('REMOTE_ADDR'),
                'user_agent': request.META.get('HTTP_USER_AGENT', '')
            }
        )

        if not created:
            consent.granted = True
            consent.granted_at = timezone.now()
            consent.revoked_at = None
            consent.save()

    def revoke_consent(self, consent_type):
        """Revoke consent"""
        try:
            consent = self.consents.get(consent_type=consent_type)
            consent.granted = False
            consent.revoked_at = timezone.now()
            consent.save()

            # Take action based on consent type
            if consent_type == ConsentType.MARKETING:
                # Unsubscribe from marketing
                self.unsubscribe_marketing()
            elif consent_type == ConsentType.ANALYTICS:
                # Stop analytics tracking
                self.disable_analytics()

        except UserConsent.DoesNotExist:
            pass

    def has_consent(self, consent_type):
        """Check if user has granted specific consent"""
        try:
            consent = self.consents.get(consent_type=consent_type)
            return consent.granted and consent.revoked_at is None
        except UserConsent.DoesNotExist:
            return False

    def export_data(self):
        """GDPR Article 15: Right of access"""
        return {
            'personal_data': {
                'email': self.email,
                'created_at': self.created_at.isoformat(),
            },
            'consents': [
                {
                    'type': c.consent_type,
                    'granted': c.granted,
                    'granted_at': c.granted_at.isoformat() if c.granted_at else None,
                    'consent_text': c.consent_text_shown
                }
                for c in self.consents.all()
            ],
            'data_access_logs': list(
                self.access_logs.values('accessed_at', 'ip_address', 'action')
            )
        }

    def delete_account(self):
        """GDPR Article 17: Right to erasure"""
        # Anonymize instead of hard delete (preserve audit trail)
        self.email = f"deleted-{self.id}@anonymized.local"
        self.deleted_at = timezone.now()
        self.save()

        # Log deletion for compliance
        DeletionLog.objects.create(
            user_id=self.id,
            deleted_at=timezone.now(),
            reason='User requested deletion (GDPR Art. 17)'
        )

# View: Signup with explicit consent
def signup(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        # Check required consents
        essential_consent = request.POST.get('consent_essential') == 'on'
        privacy_accepted = request.POST.get('privacy_policy') == 'on'

        if not essential_consent or not privacy_accepted:
            return JsonResponse({
                'error': 'Essential consent and privacy policy acceptance required'
            }, status=400)

        # Create user
        user = User.objects.create_user(
            email=email,
            password=password,
            privacy_policy_accepted_at=timezone.now(),
            data_processing_consent_version='1.0'
        )

        # Record essential consent (required)
        user.grant_consent(
            ConsentType.ESSENTIAL,
            request,
            "Process account data for service operation"
        )

        # Record optional consents
        if request.POST.get('consent_analytics') == 'on':
            user.grant_consent(
                ConsentType.ANALYTICS,
                request,
                "Collect usage analytics to improve service"
            )

        if request.POST.get('consent_marketing') == 'on':
            user.grant_consent(
                ConsentType.MARKETING,
                request,
                "Send marketing communications and newsletters"
            )

        return JsonResponse({'success': True, 'user_id': user.id})
```

### Data Breach Notification
```java
// ✅ SECURE: Data breach detection and notification
import java.time.LocalDateTime;
import java.time.Duration;

@Service
public class DataBreachService {

    @Autowired
    private NotificationService notificationService;

    @Autowired
    private ComplianceService complianceService;

    /**
     * Detect and respond to data breach
     * GDPR Article 33: 72-hour notification requirement
     */
    public void handleDataBreach(BreachEvent event) {
        // Log breach immediately
        BreachLog log = new BreachLog();
        log.setDetectedAt(LocalDateTime.now());
        log.setSeverity(assessSeverity(event));
        log.setAffectedRecords(event.getAffectedRecordCount());
        log.setBreachType(event.getType());
        log.setDataTypes(event.getExposedDataTypes());
        breachRepository.save(log);

        // Assess severity
        boolean requiresNotification = assessIfNotificationRequired(event);

        if (requiresNotification) {
            // GDPR: Notify supervisory authority within 72 hours
            Duration timeToNotify = Duration.ofHours(72);
            LocalDateTime notificationDeadline = LocalDateTime.now().plus(timeToNotify);

            log.setNotificationDeadline(notificationDeadline);
            log.setStatus(BreachStatus.NOTIFICATION_REQUIRED);

            // Notify Data Protection Officer
            notificationService.notifyDPO(log);

            // If high risk to individuals, notify affected users
            if (log.getSeverity() == BreachSeverity.HIGH) {
                List<User> affectedUsers = identifyAffectedUsers(event);
                notifyAffectedUsers(affectedUsers, log);
            }

            // Notify supervisory authority
            complianceService.notifySupervisoryAuthority(log);

            // Document breach in compliance record
            complianceService.documentBreach(log);
        }

        // Take containment actions
        containBreach(event);
    }

    private BreachSeverity assessSeverity(BreachEvent event) {
        // High risk if: PII, financial data, health data, or credentials
        if (event.getExposedDataTypes().stream()
                .anyMatch(type -> type == DataType.SSN ||
                                  type == DataType.CREDIT_CARD ||
                                  type == DataType.HEALTH_RECORD ||
                                  type == DataType.PASSWORD)) {
            return BreachSeverity.HIGH;
        }

        // Medium risk if: email, phone, address
        if (event.getAffectedRecordCount() > 1000) {
            return BreachSeverity.MEDIUM;
        }

        return BreachSeverity.LOW;
    }

    private void notifyAffectedUsers(List<User> users, BreachLog log) {
        for (User user : users) {
            EmailMessage message = new EmailMessage();
            message.setTo(user.getEmail());
            message.setSubject("Important Security Notice - Data Breach");
            message.setBody(String.format(
                "We are writing to inform you of a data security incident that may have affected your personal information.\n\n" +
                "What happened: %s\n" +
                "Data affected: %s\n" +
                "When it occurred: %s\n" +
                "Actions we're taking: %s\n" +
                "What you should do: %s\n\n" +
                "For more information, please contact our Data Protection Officer.",
                log.getBreachDescription(),
                log.getDataTypes(),
                log.getDetectedAt(),
                log.getContainmentActions(),
                log.getUserActions()
            ));

            notificationService.sendSecureEmail(message);

            // Log notification for compliance
            log.addNotifiedUser(user.getId(), LocalDateTime.now());
        }
    }
}
```

## Integration with Agents

**For comprehensive security analysis, use parallel agents**:

```javascript
// Example: Review data handling
use the .claude/agents/data-protection-specialist.md agent to validate privacy controls
use the .claude/agents/secrets-specialist.md agent to check encryption key management
use the .claude/agents/logging-specialist.md agent to verify no PII in logs
```

## Progressive Disclosure

**This overview provides the essentials. For deeper analysis, I can provide**:
- GDPR compliance checklists (Articles 5, 6, 7, 15-22, 32-34)
- CCPA compliance requirements (California Consumer Privacy Act)
- HIPAA compliance for health data (PHI protection)
- PCI-DSS compliance for payment data
- Data classification frameworks
- Encryption implementation strategies
- Data anonymization and pseudonymization techniques
- Privacy impact assessment (PIA) templates

**Security Rules**: See [rules.json](./rules.json) for complete ASVS-aligned rule specifications

---

**Related Skills**: [secrets-management](../secrets-management/SKILL.md), [logging-security](../logging-security/SKILL.md), [cryptography](../cryptography/SKILL.md)

**Standards Compliance**: ASVS V8.1-V8.3 | GDPR Articles 5, 6, 7, 15-22, 32-34 | CCPA | CWE-311, CWE-319, CWE-359, CWE-532
