from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from io import BytesIO
from datetime import datetime
from backend.models import ReportData


class PDFService:
    """Service for generating professional PDF reports"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#dc2626'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Heading style
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#dc2626'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        # Subheading style
        self.styles.add(ParagraphStyle(
            name='CustomSubHeading',
            parent=self.styles['Heading3'],
            fontSize=14,
            textColor=colors.HexColor('#000000'),
            spaceAfter=10,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        ))
        
        # Body style
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=11,
            alignment=TA_JUSTIFY,
            spaceAfter=8
        ))
        
        # Risk level styles
        for risk, color in [
            ('CRITICAL', '#7f1d1d'),
            ('HIGH', '#dc2626'),
            ('MEDIUM', '#f59e0b'),
            ('LOW', '#16a34a')
        ]:
            self.styles.add(ParagraphStyle(
                name=f'Risk{risk}',
                parent=self.styles['BodyText'],
                fontSize=16,
                textColor=colors.HexColor(color),
                fontName='Helvetica-Bold',
                alignment=TA_CENTER
            ))
    
    def _create_header(self, report_data: ReportData):
        """Create report header"""
        elements = []
        
        # Title
        title = Paragraph(
            "🔴 WEB & API RECONNAISSANCE REPORT",
            self.styles['CustomTitle']
        )
        elements.append(title)
        elements.append(Spacer(1, 0.3 * inch))
        
        # Target info table
        target_data = [
            ['Target Domain:', report_data.recon_results.domain],
            ['Scan Date:', report_data.recon_results.timestamp.strftime('%Y-%m-%d %H:%M:%S')],
            ['Scan Duration:', f"{report_data.recon_results.scan_duration:.2f} seconds"],
            ['Risk Level:', report_data.ai_analysis.risk_level]
        ]
        
        target_table = Table(target_data, colWidths=[2*inch, 4*inch])
        target_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#1f2937')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
            ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#f3f4f6')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.black),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#9ca3af')),
            ('ROWBACKGROUNDS', (1, 0), (1, -1), [colors.HexColor('#f9fafb'), colors.HexColor('#f3f4f6')]),
        ]))
        
        elements.append(target_table)
        elements.append(Spacer(1, 0.5 * inch))
        
        return elements
    
    def _create_recon_section(self, recon_results):
        """Create reconnaissance findings section"""
        elements = []
        
        # Section title
        elements.append(Paragraph("RECONNAISSANCE FINDINGS", self.styles['CustomHeading']))
        elements.append(Spacer(1, 0.2 * inch))
        
        # Subdomains
        elements.append(Paragraph("Discovered Subdomains", self.styles['CustomSubHeading']))
        subdomain_text = f"Total: {len(recon_results.subdomains)}<br/><br/>"
        subdomain_text += "<br/>".join([f"• {sd}" for sd in recon_results.subdomains[:30]])
        if len(recon_results.subdomains) > 30:
            subdomain_text += f"<br/>... and {len(recon_results.subdomains) - 30} more"
        elements.append(Paragraph(subdomain_text, self.styles['CustomBody']))
        elements.append(Spacer(1, 0.3 * inch))
        
        # Live hosts
        elements.append(Paragraph("Live Hosts", self.styles['CustomSubHeading']))
        host_text = f"Total: {len(recon_results.live_hosts)}<br/><br/>"
        host_text += "<br/>".join([f"• {host}" for host in recon_results.live_hosts[:20]])
        if len(recon_results.live_hosts) > 20:
            host_text += f"<br/>... and {len(recon_results.live_hosts) - 20} more"
        elements.append(Paragraph(host_text, self.styles['CustomBody']))
        elements.append(Spacer(1, 0.3 * inch))
        
        # Open ports
        if recon_results.open_ports:
            elements.append(Paragraph("Open Ports", self.styles['CustomSubHeading']))
            port_data = [['Host', 'Open Ports']]
            for host, ports in list(recon_results.open_ports.items())[:15]:
                port_data.append([host, ', '.join(map(str, ports))])
            
            port_table = Table(port_data, colWidths=[3*inch, 3*inch])
            port_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#9ca3af')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
            ]))
            elements.append(port_table)
            elements.append(Spacer(1, 0.3 * inch))
        
        # Technologies
        if recon_results.technologies:
            elements.append(Paragraph("Detected Technologies", self.styles['CustomSubHeading']))
            tech_data = [['Host', 'Technologies']]
            for host, techs in list(recon_results.technologies.items())[:15]:
                tech_data.append([host, ', '.join(techs)])
            
            tech_table = Table(tech_data, colWidths=[2.5*inch, 3.5*inch])
            tech_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#9ca3af')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
            ]))
            elements.append(tech_table)
            elements.append(Spacer(1, 0.3 * inch))
        
        # Endpoints
        elements.append(Paragraph("Discovered Endpoints", self.styles['CustomSubHeading']))
        endpoint_text = f"Total: {len(recon_results.endpoints)}<br/><br/>"
        endpoint_text += "<br/>".join([f"• {ep}" for ep in recon_results.endpoints[:25]])
        if len(recon_results.endpoints) > 25:
            endpoint_text += f"<br/>... and {len(recon_results.endpoints) - 25} more"
        elements.append(Paragraph(endpoint_text, self.styles['CustomBody']))
        elements.append(Spacer(1, 0.3 * inch))
        
        # Directories
        if recon_results.directories:
            elements.append(Paragraph("Discovered Directories", self.styles['CustomSubHeading']))
            dir_text = "<br/>".join([f"• {d}" for d in recon_results.directories])
            elements.append(Paragraph(dir_text, self.styles['CustomBody']))
        
        elements.append(PageBreak())
        
        return elements
    
    def _create_ai_analysis_section(self, ai_analysis):
        """Create AI analysis section"""
        elements = []
        
        # Section title
        elements.append(Paragraph("AI-POWERED SECURITY ANALYSIS", self.styles['CustomHeading']))
        elements.append(Spacer(1, 0.2 * inch))
        
        # Risk level
        elements.append(Paragraph("Overall Risk Assessment", self.styles['CustomSubHeading']))
        risk_style = f'Risk{ai_analysis.risk_level}'
        elements.append(Paragraph(ai_analysis.risk_level, self.styles[risk_style]))
        elements.append(Spacer(1, 0.3 * inch))
        
        # Attack surface summary
        elements.append(Paragraph("Attack Surface Summary", self.styles['CustomSubHeading']))
        elements.append(Paragraph(ai_analysis.attack_surface_summary, self.styles['CustomBody']))
        elements.append(Spacer(1, 0.3 * inch))
        
        # Possible vulnerabilities
        elements.append(Paragraph("Possible Vulnerabilities", self.styles['CustomSubHeading']))
        vuln_text = "<br/><br/>".join([f"<b>{i+1}.</b> {vuln}" 
                                       for i, vuln in enumerate(ai_analysis.possible_vulnerabilities)])
        elements.append(Paragraph(vuln_text, self.styles['CustomBody']))
        elements.append(Spacer(1, 0.3 * inch))
        
        # Interesting endpoints
        elements.append(Paragraph("Interesting Endpoints for Further Investigation", 
                                 self.styles['CustomSubHeading']))
        endpoint_text = "<br/><br/>".join([f"<b>{i+1}.</b> {ep}" 
                                          for i, ep in enumerate(ai_analysis.interesting_endpoints)])
        elements.append(Paragraph(endpoint_text, self.styles['CustomBody']))
        elements.append(Spacer(1, 0.3 * inch))
        
        # Security recommendations
        elements.append(Paragraph("Security Recommendations", self.styles['CustomSubHeading']))
        rec_text = "<br/><br/>".join([f"<b>{i+1}.</b> {rec}" 
                                     for i, rec in enumerate(ai_analysis.security_recommendations)])
        elements.append(Paragraph(rec_text, self.styles['CustomBody']))
        elements.append(Spacer(1, 0.3 * inch))
        
        # Detailed analysis
        elements.append(Paragraph("Detailed Security Analysis", self.styles['CustomSubHeading']))
        elements.append(Paragraph(ai_analysis.detailed_analysis, self.styles['CustomBody']))
        
        return elements
    
    def _create_footer(self):
        """Create report footer"""
        elements = []
        
        elements.append(PageBreak())
        elements.append(Spacer(1, 2 * inch))
        
        footer_text = """
        <para align=center>
        <b>DISCLAIMER</b><br/><br/>
        This reconnaissance report is for educational and authorized security testing purposes only.
        Unauthorized access to computer systems is illegal. Always obtain proper authorization
        before conducting security assessments.<br/><br/>
        Generated by AI-Powered Recon Tool<br/>
        </para>
        """
        
        elements.append(Paragraph(footer_text, self.styles['CustomBody']))
        
        return elements
    
    def generate_report(self, report_data: ReportData) -> BytesIO:
        """
        Generate complete PDF report
        
        Args:
            report_data: Complete report data
            
        Returns:
            BytesIO buffer containing PDF
        """
        print("[*] Generating PDF report...")
        
        # Create buffer
        buffer = BytesIO()
        
        # Create document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        # Build document content
        story = []
        
        # Add sections
        story.extend(self._create_header(report_data))
        story.extend(self._create_recon_section(report_data.recon_results))
        story.extend(self._create_ai_analysis_section(report_data.ai_analysis))
        story.extend(self._create_footer())
        
        # Build PDF
        doc.build(story)
        
        # Reset buffer position
        buffer.seek(0)
        
        print("[✓] PDF report generated successfully")
        return buffer
