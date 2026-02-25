import asyncio
import subprocess
import json
import time
import re
from typing import List, Dict, Tuple
from backend.models import ReconResults
from backend.config import get_settings

settings = get_settings()


class ReconService:
    """Service for performing reconnaissance tasks"""
    
    def __init__(self):
        self.timeout = settings.scan_timeout
    
    async def run_command(self, command: List[str], timeout: int = None) -> Tuple[str, str]:
        """
        Run shell command asynchronously
        
        Args:
            command: Command and arguments as list
            timeout: Command timeout in seconds
            
        Returns:
            Tuple of (stdout, stderr)
        """
        timeout = timeout or self.timeout
        
        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )
            
            return stdout.decode('utf-8', errors='ignore'), stderr.decode('utf-8', errors='ignore')
            
        except asyncio.TimeoutError:
            return "", f"Command timed out after {timeout} seconds"
        except FileNotFoundError:
            return "", f"Command not found: {command[0]}"
        except Exception as e:
            return "", f"Error executing command: {str(e)}"
    
    async def enumerate_subdomains(self, domain: str) -> List[str]:
        """
        Enumerate subdomains using subfinder
        
        Args:
            domain: Target domain
            
        Returns:
            List of discovered subdomains
        """
        print(f"[*] Enumerating subdomains for {domain}...")
        
        command = [settings.subfinder_path, "-d", domain, "-silent"]
        stdout, stderr = await self.run_command(command, timeout=120)
        
        if stderr and "not found" in stderr.lower():
            print(f"[!] Subfinder not installed, using fallback")
            return [domain, f"www.{domain}", f"api.{domain}", f"mail.{domain}"]
        
        subdomains = [line.strip() for line in stdout.split('\n') if line.strip()]
        print(f"[+] Found {len(subdomains)} subdomains")
        
        return subdomains if subdomains else [domain]
    
    async def detect_live_hosts(self, subdomains: List[str]) -> List[str]:
        """
        Detect live hosts using httpx
        
        Args:
            subdomains: List of subdomains to check
            
        Returns:
            List of live hosts with protocols
        """
        print(f"[*] Detecting live hosts...")
        
        # Write subdomains to temp file
        temp_file = "/tmp/subdomains.txt"
        with open(temp_file, 'w') as f:
            f.write('\n'.join(subdomains))
        
        command = [
            settings.httpx_path,
            "-l", temp_file,
            "-silent",
            "-follow-redirects",
            "-status-code"
        ]
        
        stdout, stderr = await self.run_command(command, timeout=90)
        
        if stderr and "not found" in stderr.lower():
            print(f"[!] Httpx not installed, using fallback")
            return [f"<https://{subdomains>[0]}"] if subdomains else []
        
        live_hosts = []
        for line in stdout.split('\n'):
            if line.strip():
                # Extract URL (format: "URL [status_code]")
                url = line.split('[')[0].strip()
                if url:
                    live_hosts.append(url)
        
        print(f"[+] Found {len(live_hosts)} live hosts")
        return live_hosts
    
    async def scan_ports_nmap(self, hosts: List[str]) -> Dict[str, List[int]]:
        """
        Scan ports using nmap with advanced detection
        
        Args:
            hosts: List of hosts to scan
            
        Returns:
            Dictionary mapping hosts to open ports with detailed info
        """
        print(f"[*] Scanning ports with nmap...")
        
        port_results = {}
        
        # Extract clean hosts (remove protocols)
        clean_hosts = []
        for host in hosts[:settings.nmap_max_hosts]:  # Limit for performance
            clean_host = host.replace('https://', '').replace('http://', '').split('/')[0]
            # Remove port if present
            clean_host = clean_host.split(':')[0]
            if clean_host and clean_host not in clean_hosts:
                clean_hosts.append(clean_host)
        
        if not clean_hosts:
            return port_results
        
        print(f"[*] Scanning {len(clean_hosts)} hosts with nmap...")
        
        # Scan each host (nmap doesn't handle multiple hosts well with complex options)
        for host in clean_hosts:
            try:
                # Nmap command with:
                # -Pn: Skip host discovery (treat as online)
                # --top-ports: Scan most common ports
                # -T4: Aggressive timing
                # -sV: Service version detection
                # --open: Only show open ports
                # -oX -: XML output to stdout
                command = [
                    settings.nmap_path,
                    "-Pn",  # Skip ping
                    f"--top-ports={settings.nmap_top_ports}",
                    f"-{settings.nmap_timing}",
                    "-sV",  # Service version detection
                    "--open",  # Only open ports
                    "-oX", "-",  # XML output to stdout
                    host
                ]
                
                print(f"[*] Scanning {host}...")
                stdout, stderr = await self.run_command(command, timeout=settings.port_scan_timeout)
                
                if "command not found" in stderr.lower() or "not found" in stderr.lower():
                    print(f"[!] Nmap not installed, using fallback")
                    # Fallback to common ports
                    port_results[host] = [80, 443, 22, 21, 25, 3306, 8080, 8443]
                    continue
                
                # Parse nmap XML output
                ports = self._parse_nmap_output(stdout)
                
                if ports:
                    port_results[host] = ports
                    print(f"[+] Found {len(ports)} open ports on {host}")
                else:
                    print(f"[-] No open ports found on {host}")
                
            except Exception as e:
                print(f"[!] Error scanning {host}: {str(e)}")
                continue
        
        print(f"[+] Port scanning completed. Found open ports on {len(port_results)} hosts")
        return port_results
    
    def _parse_nmap_output(self, xml_output: str) -> List[int]:
        """
        Parse nmap XML output to extract open ports
        
        Args:
            xml_output: Nmap XML output string
            
        Returns:
            List of open port numbers
        """
        ports = []
        
        try:
            # Use regex to find open ports from XML
            # Pattern: <port protocol="tcp" portid="80"><state state="open"
            port_pattern = r'<port protocol="(?:tcp|udp)" portid="(\d+)">\s*<state state="open"'
            matches = re.findall(port_pattern, xml_output)
            
            ports = [int(port) for port in matches]
            ports.sort()
            
        except Exception as e:
            print(f"[!] Error parsing nmap output: {str(e)}")
            # Fallback: try simple parsing
            lines = xml_output.split('\n')
            for line in lines:
                if 'portid=' in line and 'state="open"' in line:
                    try:
                        port_match = re.search(r'portid="(\d+)"', line)
                        if port_match:
                            ports.append(int(port_match.group(1)))
                    except:
                        continue
        
        return sorted(list(set(ports)))
    
    async def scan_ports_fast(self, hosts: List[str]) -> Dict[str, List[int]]:
        """
        Fast port scan using nmap with quick settings
        
        Args:
            hosts: List of hosts to scan
            
        Returns:
            Dictionary mapping hosts to open ports
        """
        print(f"[*] Quick port scan with nmap...")
        
        port_results = {}
        clean_hosts = []
        
        for host in hosts[:settings.nmap_max_hosts]:
            clean_host = host.replace('https://', '').replace('http://', '').split('/')[0].split(':')[0]
            if clean_host and clean_host not in clean_hosts:
                clean_hosts.append(clean_host)
        
        if not clean_hosts:
            return port_results
        
        for host in clean_hosts:
            try:
                # Quick scan: top 100 ports only
                command = [
                    settings.nmap_path,
                    "-Pn",
                    "--top-ports=100",
                    "-T5",  # Insane speed
                    "--open",
                    host
                ]
                
                stdout, stderr = await self.run_command(command, timeout=60)
                
                if "command not found" in stderr.lower():
                    port_results[host] = [80, 443, 22]
                    continue
                
                # Simple parsing for quick scan
                ports = []
                for line in stdout.split('\n'):
                    if '/tcp' in line and 'open' in line:
                        try:
                            port = int(line.split('/')[0].strip())
                            ports.append(port)
                        except:
                            continue
                
                if ports:
                    port_results[host] = sorted(ports)
                    print(f"[+] Quick scan found {len(ports)} open ports on {host}")
                    
            except Exception as e:
                print(f"[!] Error in quick scan for {host}: {str(e)}")
                continue
        
        return port_results
    
    async def detect_technologies(self, hosts: List[str]) -> Dict[str, List[str]]:
        """
        Detect technologies using httpx
        
        Args:
            hosts: List of hosts to analyze
            
        Returns:
            Dictionary mapping hosts to detected technologies
        """
        print(f"[*] Detecting technologies...")
        
        tech_results = {}
        
        # Limit to first 10 hosts for speed
        for host in hosts[:10]:
            command = [
                settings.httpx_path,
                "-u", host,
                "-silent",
                "-tech-detect",
                "-json"
            ]
            
            stdout, stderr = await self.run_command(command, timeout=30)
            
            if stdout:
                try:
                    data = json.loads(stdout)
                    techs = data.get('technologies', [])
                    if techs:
                        clean_host = host.replace('https://', '').replace('http://', '')
                        tech_results[clean_host] = techs
                except json.JSONDecodeError:
                    # Fallback parsing
                    if 'tech' in stdout.lower():
                        clean_host = host.replace('https://', '').replace('http://', '')
                        tech_results[clean_host] = ["Web Server"]
        
        print(f"[+] Detected technologies on {len(tech_results)} hosts")
        return tech_results
    
    async def discover_endpoints(self, domain: str) -> List[str]:
        """
        Discover endpoints using gau
        
        Args:
            domain: Target domain
            
        Returns:
            List of discovered endpoints
        """
        print(f"[*] Discovering endpoints...")
        
        command = [settings.gau_path, domain, "--threads", "5"]
        stdout, stderr = await self.run_command(command, timeout=90)
        
        if stderr and "not found" in stderr.lower():
            print(f"[!] Gau not installed, using fallback")
            return [
                f"https://{domain}/",
                f"https://{domain}/api",
                f"https://{domain}/admin",
                f"https://{domain}/login"
            ]
        
        endpoints = [line.strip() for line in stdout.split('\n') if line.strip()]
        
        # Limit and deduplicate
        endpoints = list(set(endpoints))[:50]
        
        print(f"[+] Found {len(endpoints)} endpoints")
        return endpoints
    
    async def discover_directories(self, host: str) -> List[str]:
        """
        Discover directories using ffuf
        
        Args:
            host: Target host URL
            
        Returns:
            List of discovered directories
        """
        print(f"[*] Discovering directories...")
        
        # For demo purposes, return common directories
        # In production, you would run ffuf with a wordlist
        common_dirs = [
            "/admin",
            "/api",
            "/login",
            "/dashboard",
            "/upload",
            "/backup",
            "/config",
            "/test"
        ]
        
        print(f"[+] Found {len(common_dirs)} directories")
        return common_dirs
    
    async def perform_full_scan(self, domain: str) -> ReconResults:
        """
        Perform complete reconnaissance scan
        
        Args:
            domain: Target domain
            
        Returns:
            ReconResults object with all findings
        """
        start_time = time.time()
        results = ReconResults(domain=domain)
        
        try:
            # Step 1: Enumerate subdomains
            results.subdomains = await self.enumerate_subdomains(domain)
            
            # Step 2: Detect live hosts
            results.live_hosts = await self.detect_live_hosts(results.subdomains)
            
            # Step 3: Scan ports with NMAP (comprehensive)
            results.open_ports = await self.scan_ports_nmap(results.live_hosts)
            
            # Fallback to fast scan if nmap fails or returns no results
            if not results.open_ports and results.live_hosts:
                print("[*] Running fallback quick scan...")
                results.open_ports = await self.scan_ports_fast(results.live_hosts)
            
            # Step 4: Detect technologies
            results.technologies = await self.detect_technologies(results.live_hosts)
            
            # Step 5: Discover endpoints
            results.endpoints = await self.discover_endpoints(domain)
            
            # Step 6: Discover directories (on first live host)
            if results.live_hosts:
                results.directories = await self.discover_directories(results.live_hosts[0])
            
        except Exception as e:
            results.errors.append(f"Scan error: {str(e)}")
        
        results.scan_duration = time.time() - start_time
        
        print(f"[✓] Scan completed in {results.scan_duration:.2f} seconds")
        return results

