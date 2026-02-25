import httpx
import json
from typing import Dict, Any
from backend.models import ReconResults, AIAnalysis
from backend.config import get_settings

settings = get_settings()


class AIService:
    """Service for AI-powered analysis using Perplexity API"""
    
    def __init__(self):
        self.api_key = settings.perplexity_api_key
        self.api_url = settings.perplexity_api_url
        self.model = settings.perplexity_model
        self.timeout = settings.ai_timeout
    
    def _build_analysis_prompt(self, recon_data: ReconResults) -> str:
        """
        Build comprehensive prompt for AI analysis
        
        Args:
            recon_data: Reconnaissance results
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""You are a senior cybersecurity analyst. Analyze the following reconnaissance data for the domain "{recon_data.domain}" and provide a comprehensive security assessment.

RECONNAISSANCE DATA:
-------------------

Subdomains Found: {len(recon_data.subdomains)}
{json.dumps(recon_data.subdomains[:20], indent=2)}

Live Hosts: {len(recon_data.live_hosts)}
{json.dumps(recon_data.live_hosts[:15], indent=2)}

Open Ports by Host:
{json.dumps(recon_data.open_ports, indent=2)}

Technologies Detected:
{json.dumps(recon_data.technologies, indent=2)}

Endpoints Discovered: {len(recon_data.endpoints)}
{json.dumps(recon_data.endpoints[:30], indent=2)}

Directories Found:
{json.dumps(recon_data.directories, indent=2)}

REQUIRED ANALYSIS:
-----------------

Provide your analysis in the following JSON format:

{{
  "attack_surface_summary": "Brief overview of the attack surface (2-3 sentences)",
  "possible_vulnerabilities": [
    "List 5-8 specific potential vulnerabilities based on the data",
    "Include both technical and configuration issues",
    "Be specific and actionable"
  ],
  "interesting_endpoints": [
    "List 5-10 endpoints that warrant further investigation",
    "Explain why each is interesting from a security perspective"
  ],
  "security_recommendations": [
    "Provide 8-12 specific, actionable security recommendations",
    "Prioritize by potential impact",
    "Include both quick wins and strategic improvements"
  ],
  "risk_level": "Assess overall risk as: LOW, MEDIUM, HIGH, or CRITICAL",
  "detailed_analysis": "Provide 4-5 paragraphs of detailed security analysis covering: attack vectors, exposed services, technology stack risks, and remediation priorities"
}}

IMPORTANT: Return ONLY the JSON object, no additional text or formatting."""

        return prompt
    
    async def analyze_recon_results(self, recon_data: ReconResults) -> AIAnalysis:
        """
        Analyze reconnaissance results using Perplexity AI
        
        Args:
            recon_data: Reconnaissance results to analyze
            
        Returns:
            AIAnalysis object with security assessment
        """
        print("[*] Sending data to Perplexity AI for analysis...")
        
        prompt = self._build_analysis_prompt(recon_data)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert cybersecurity analyst specializing in web application security, penetration testing, and vulnerability assessment. Provide detailed, actionable security analysis."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.2,
            "max_tokens": 4000
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.api_url,
                    headers=headers,
                    json=payload
                )
                
                response.raise_for_status()
                data = response.json()
                
                # Extract content from response
                content = data["choices"][0]["message"]["content"]
                
                # Parse JSON from content
                # Remove markdown code blocks if present
                content = content.strip()
                if content.startswith("```json"):
                    content = content[7:]
                if content.startswith("```"):
                    content = content[3:]
                if content.endswith("```"):
                    content = content[:-3]
                
                analysis_data = json.loads(content.strip())
                
                # Create AIAnalysis object
                analysis = AIAnalysis(**analysis_data)
                
                print("[✓] AI analysis completed successfully")
                return analysis
                
        except httpx.HTTPStatusError as e:
            print(f"[!] HTTP error from Perplexity API: {e}")
            return self._fallback_analysis(recon_data)
        except json.JSONDecodeError as e:
            print(f"[!] Failed to parse AI response: {e}")
            return self._fallback_analysis(recon_data)
        except Exception as e:
            print(f"[!] Error during AI analysis: {e}")
            return self._fallback_analysis(recon_data)
    
    def _fallback_analysis(self, recon_data: ReconResults) -> AIAnalysis:
        """
        Provide fallback analysis if AI service fails
        
        Args:
            recon_data: Reconnaissance results
            
        Returns:
            Basic AIAnalysis object
        """
        print("[!] Using fallback analysis due to AI service error")
        
        # Determine risk level based on findings
        risk_factors = 0
        if len(recon_data.subdomains) > 20:
            risk_factors += 1
        if len(recon_data.live_hosts) > 10:
            risk_factors += 1
        if any(len(ports) > 5 for ports in recon_data.open_ports.values()):
            risk_factors += 2
        
        risk_level = "LOW"
        if risk_factors >= 4:
            risk_level = "CRITICAL"
        elif risk_factors >= 3:
            risk_level = "HIGH"
        elif risk_factors >= 2:
            risk_level = "MEDIUM"
        
        return AIAnalysis(
            attack_surface_summary=f"The domain {recon_data.domain} has {len(recon_data.subdomains)} subdomains and {len(recon_data.live_hosts)} live hosts, representing a moderate attack surface.",
            possible_vulnerabilities=[
                "Exposed administrative interfaces may be accessible without proper authentication",
                "Multiple open ports could indicate unnecessary services running",
                "Subdomain enumeration reveals potential forgotten or development environments",
                "Technology fingerprints expose version information useful for targeted attacks",
                "Common directory patterns suggest default configurations may be in use"
            ],
            interesting_endpoints=[
                f"{endpoint} - Requires further investigation" 
                for endpoint in recon_data.endpoints[:5]
            ] if recon_data.endpoints else ["No endpoints discovered for analysis"],
            security_recommendations=[
                "Implement strong authentication on all administrative interfaces",
                "Close unnecessary ports and disable unused services",
                "Remove or secure development and staging subdomains",
                "Update web technologies to latest stable versions",
                "Implement Web Application Firewall (WAF) rules",
                "Enable HTTPS across all subdomains with HSTS",
                "Conduct regular vulnerability assessments",
                "Implement proper access controls and least privilege"
            ],
            risk_level=risk_level,
            detailed_analysis=f"The reconnaissance of {recon_data.domain} reveals a typical web application infrastructure with multiple entry points. The presence of {len(recon_data.subdomains)} subdomains and {len(recon_data.live_hosts)} active hosts indicates a distributed architecture. Security priorities should focus on reducing the attack surface, implementing proper access controls, and ensuring all exposed services are properly configured and updated."
        )
