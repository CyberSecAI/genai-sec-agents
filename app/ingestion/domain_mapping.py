"""
Domain mapping configuration for ASVS-to-domain integration.

This module defines the comprehensive mapping between ASVS verification sections
and security domains for the domain-based Rule Card organization system.
"""

from typing import Dict, List
from dataclasses import dataclass

@dataclass
class DomainMapping:
    """Configuration for mapping ASVS sections to security domains."""
    asvs_sections: List[str]
    owasp_topics: List[str] 
    description: str
    priority: int  # 1=highest, 3=lowest

# Comprehensive domain taxonomy based on ASVS 5.0 structure
DOMAIN_MAPPINGS: Dict[str, DomainMapping] = {
    # Priority 1 - Core Security Domains (8 domains)
    "authentication": DomainMapping(
        asvs_sections=["V6", "V9", "V10"], 
        owasp_topics=["authentication", "session_management"],
        description="User authentication and identity verification",
        priority=1
    ),
    
    "authorization": DomainMapping(
        asvs_sections=["V8"],
        owasp_topics=["authorization", "access_control"], 
        description="Access control and privilege management",
        priority=1
    ),
    
    "cryptography": DomainMapping(
        asvs_sections=["V11"],
        owasp_topics=["cryptography", "key_management", "hashing", "encryption"],
        description="Cryptographic implementation and key management", 
        priority=1
    ),
    
    "input_validation": DomainMapping(
        asvs_sections=["V1", "V2"],
        owasp_topics=["input_validation", "sql_injection_prevention", "business_logic"],
        description="Input validation and business logic security",
        priority=1
    ),
    
    "session_management": DomainMapping(
        asvs_sections=["V7"],
        owasp_topics=["session_management", "authentication"],
        description="Session lifecycle and security",
        priority=1
    ),
    
    "api_security": DomainMapping(
        asvs_sections=["V4"], 
        owasp_topics=["api_security", "rest_security"],
        description="REST, GraphQL, and web service security",
        priority=1
    ),
    
    "data_protection": DomainMapping(
        asvs_sections=["V14"],
        owasp_topics=["data_protection", "privacy"],
        description="Privacy and data handling requirements",
        priority=1
    ),
    
    "secure_communication": DomainMapping(
        asvs_sections=["V12"],
        owasp_topics=["transport_layer_security", "network_security"],
        description="TLS and network security",
        priority=1
    ),
    
    # Priority 2 - Specialized Domains (4 domains)
    "web_security": DomainMapping(
        asvs_sections=["V3", "V17"],
        owasp_topics=["web_security", "frontend_security"],
        description="Frontend and client-side security including WebRTC",
        priority=2
    ),
    
    "file_handling": DomainMapping(
        asvs_sections=["V5"],
        owasp_topics=["file_upload", "file_security"],
        description="File upload and processing security", 
        priority=2
    ),
    
    "configuration": DomainMapping(
        asvs_sections=["V13"],
        owasp_topics=["security_configuration", "hardening"],
        description="Security configuration and hardening",
        priority=2
    ),
    
    "logging": DomainMapping(
        asvs_sections=["V16"],
        owasp_topics=["logging", "error_handling"],
        description="Security logging and error handling",
        priority=2
    ),
    
    # Priority 3 - Advanced Topics (2 domains)  
    "secure_coding": DomainMapping(
        asvs_sections=["V15"],
        owasp_topics=["secure_coding", "architectural_patterns"],
        description="Architectural patterns and development practices",
        priority=3
    ),
    
    "network_security": DomainMapping(
        asvs_sections=["V12"],  # Additional network requirements beyond TLS
        owasp_topics=["network_security", "infrastructure_security"],
        description="Advanced network-layer protections",
        priority=3
    )
}

def get_domain_for_asvs_section(asvs_section: str) -> str:
    """
    Get the primary domain for a given ASVS section.
    
    Args:
        asvs_section: ASVS section identifier (e.g., 'V11', 'V6')
        
    Returns:
        Domain name or 'unknown' if not found
    """
    for domain, mapping in DOMAIN_MAPPINGS.items():
        if asvs_section in mapping.asvs_sections:
            return domain
    return "unknown"

def get_priority_domains(priority: int) -> List[str]:
    """
    Get all domains for a specific priority level.
    
    Args:
        priority: Priority level (1=highest, 3=lowest)
        
    Returns:
        List of domain names for that priority
    """
    return [domain for domain, mapping in DOMAIN_MAPPINGS.items() 
            if mapping.priority == priority]

def get_all_domains() -> List[str]:
    """Get all defined security domains."""
    return list(DOMAIN_MAPPINGS.keys())

def validate_domain_mapping() -> Dict[str, List[str]]:
    """
    Validate domain mapping for completeness and conflicts.
    
    Returns:
        Dictionary with any validation issues found
    """
    issues = {"missing_sections": [], "duplicate_sections": []}
    
    # Check for ASVS sections V1-V17 coverage
    all_sections = set()
    for mapping in DOMAIN_MAPPINGS.values():
        for section in mapping.asvs_sections:
            if section in all_sections:
                issues["duplicate_sections"].append(section)
            all_sections.add(section)
    
    # Check for missing V1-V17 coverage
    expected_sections = {f"V{i}" for i in range(1, 18)}
    missing = expected_sections - all_sections
    issues["missing_sections"] = list(missing)
    
    return issues