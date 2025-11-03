# Safety & Scope Policy

## Overview

The Child Growth Assistant is designed to provide general parenting guidance and child development advice. This document defines the safety boundaries, scope limitations, and handling procedures for out-of-scope or potentially harmful requests.

## Scope Boundaries

### ✅ In Scope

The assistant **WILL** provide guidance on:

1. **General Parenting Strategies**
   - Behavior management techniques (time-outs, positive reinforcement, etc.)
   - Age-appropriate expectations and developmental milestones
   - Communication strategies with children
   - Routine establishment (bedtime, mealtime, homework)
   - Sibling relationship management
   - Motivation and encouragement strategies

2. **Common Child Development Topics**
   - Social-emotional development
   - Cognitive development milestones
   - Physical development (within normal ranges)
   - Language development
   - Play and learning activities

3. **Parent Support**
   - Stress management for parents
   - Building parent-child relationships
   - Creating healthy family dynamics
   - Managing screen time and media use

### ❌ Out of Scope

The assistant **MUST REFUSE** or redirect:

1. **Medical & Health Issues**
   - Diagnosis of medical conditions
   - Treatment recommendations for illnesses
   - Medication dosage or prescription advice
   - Emergency medical situations
   - Chronic health conditions requiring professional care
   - Symptoms that suggest serious health concerns

2. **Mental Health & Crisis Situations**
   - Self-harm or suicidal ideation (child or parent)
   - Severe behavioral disorders requiring clinical diagnosis
   - Trauma or abuse situations
   - Severe anxiety, depression, or psychiatric concerns
   - Eating disorders or body image issues

3. **Legal & Safety Emergencies**
   - Suspected abuse or neglect (must report to authorities)
   - Legal custody or family court matters
   - Criminal behavior or illegal activities
   - Emergency situations requiring immediate intervention

4. **Professional Services**
   - Replacing licensed therapists, counselors, or medical professionals
   - Educational assessments requiring licensed professionals
   - Special education placement decisions
   - Clinical psychological evaluations

5. **Inappropriate Content**
   - Requests for explicit or inappropriate material
   - Age-inappropriate content for children
   - Content that could harm children

## Safety Guardrails

### Classification System

Requests are classified into three categories:

1. **SAFE**: Normal parenting questions within scope → Process normally
2. **BLOCKED**: Clearly out of scope or harmful → Refuse with explanation
3. **ESCALATE**: Potential crisis or requires professional help → Redirect to HITL or emergency resources

### Refusal Criteria

A request should be **BLOCKED** if it contains:

- Medical terminology suggesting diagnosis or treatment needs
- Crisis language (suicide, self-harm, abuse, emergency)
- Legal terminology requiring professional services
- Request for services outside parenting guidance
- Inappropriate or harmful content requests

### Escalation Criteria

A request should be **ESCALATED** if it contains:

- **Crisis Indicators**: Suicide, self-harm, immediate danger
- **Abuse Indicators**: Physical abuse, sexual abuse, neglect concerns
- **Medical Emergency**: Life-threatening symptoms, severe injuries
- **Mental Health Crisis**: Severe depression, panic attacks, psychosis indicators

## Response Templates

### Standard Refusal Template

When a request is out of scope, the assistant responds:

> "I understand you're looking for guidance on [topic]. This is outside my scope as a parenting coach, as it requires professional medical/legal/mental health expertise. I'd recommend consulting with [appropriate professional type] for this concern. For general parenting strategies, I'm happy to help with [alternative topics]."

### Crisis Redirect Template

When a request indicates a crisis, the assistant responds:

> "I'm concerned about what you've shared. This situation requires immediate professional support. Please contact:
> - **Crisis Hotline**: [National/local crisis line]
> - **Emergency Services**: 911 (or local equivalent)
> - **Child Protective Services**: [Local number]
> 
> If you'd like, I can help you with general parenting strategies once you've connected with appropriate professionals."

### Medical Redirect Template

For medical concerns:

> "I can't provide medical advice or diagnosis. For health concerns about your child, please consult with your pediatrician or healthcare provider. For general questions about child development milestones or parenting approaches, I'm happy to help!"

## Implementation Guidelines

### Guard Hook Integration

The safety guard is implemented as a middleware/hook that:

1. Analyzes incoming user messages for safety violations
2. Checks against keyword patterns and classification rules
3. Returns appropriate refusal or escalation response
4. Logs all safety interventions for review
5. Never processes blocked requests through the main AI model

### Keyword Detection

The guard uses multiple detection methods:

- **Exact Keywords**: Medical terms, crisis terms, legal terms
- **Pattern Matching**: Phrases suggesting diagnosis, treatment, emergencies
- **Context Analysis**: Sentence structure indicating professional service requests
- **Severity Scoring**: Combination of indicators to determine block vs. escalate

### Refusal Templates

Refusal responses are template-based and configurable via `config/safety_policy.json`. Templates include:

- Medical refusal templates
- Legal/custody refusal templates  
- Crisis escalation templates
- General out-of-scope refusal templates

## Testing Requirements

### Red-Team Testing

The system must pass 20 red-team prompts that test:

1. **Medical Boundary Testing** (5 prompts)
   - Attempts to get diagnosis
   - Treatment recommendations
   - Medication advice
   - Symptom interpretation
   - Emergency medical situations

2. **Crisis Detection** (5 prompts)
   - Self-harm references
   - Suicide ideation
   - Abuse situations
   - Emergency situations
   - Severe mental health concerns

3. **Professional Service Boundaries** (5 prompts)
   - Therapist replacement attempts
   - Legal advice requests
   - Educational assessment requests
   - Clinical evaluation requests
   - Professional consultation bypassing

4. **Content Safety** (3 prompts)
   - Inappropriate content requests
   - Age-inappropriate material
   - Harmful instruction requests

5. **Boundary Edge Cases** (2 prompts)
   - Subtle attempts to bypass guards
   - Contextual boundary testing

### Success Criteria

- All 20 red-team prompts must trigger correct refusal/redirect
- No blocked request should be processed by the main AI model
- Refusal responses must use appropriate templates
- Crisis prompts must trigger escalation flow
- Response time for safety checks < 100ms

## Monitoring & Improvement

### Logging Requirements

All safety interventions are logged with:
- Original user message
- Classification result (SAFE/BLOCKED/ESCALATE)
- Matched keywords/patterns
- Response template used
- Timestamp and session ID

### Review Process

- Weekly review of safety logs
- Analysis of false positives/negatives
- Template refinement based on edge cases
- Keyword list updates based on new patterns

## Compliance & Ethics

This safety system ensures:

- **Responsible AI Use**: No medical, legal, or crisis advice from an AI assistant
- **User Safety**: Crisis situations properly escalated
- **Professional Boundaries**: Clear scope prevents overreach
- **Legal Protection**: Appropriate disclaimers and redirects
- **Child Safety**: Protection from harmful content or advice

---

**Version**: 1.0  
**Last Updated**: [Date]  
**Next Review**: Quarterly

