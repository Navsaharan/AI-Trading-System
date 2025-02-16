from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from fpdf import FPDF
import xlsxwriter
from ..models.model_manager import ModelManager
from ..analysis.market_analysis import MarketAnalysis

class ReportGenerator:
    """Generate detailed Excel and PDF reports for trading analysis."""
    
    def __init__(self):
        self.model_manager = ModelManager()
        self.market_analysis = MarketAnalysis()
    
    async def generate_excel_report(self, data: Dict,
                                  report_type: str) -> Dict:
        """Generate detailed Excel report with multiple sheets."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"trading_report_{report_type}_{timestamp}.xlsx"
            
            # Create Excel writer
            writer = pd.ExcelWriter(filename, engine='xlsxwriter')
            workbook = writer.book
            
            # Add formats
            header_format = workbook.add_format({
                'bold': True,
                'font_color': 'white',
                'bg_color': '#0066cc',
                'border': 1
            })
            
            number_format = workbook.add_format({
                'num_format': '#,##0.00',
                'border': 1
            })
            
            percent_format = workbook.add_format({
                'num_format': '0.00%',
                'border': 1
            })
            
            date_format = workbook.add_format({
                'num_format': 'yyyy-mm-dd hh:mm:ss',
                'border': 1
            })
            
            # Generate sheets based on report type
            if report_type == "portfolio":
                self._create_portfolio_sheets(
                    writer,
                    data,
                    header_format,
                    number_format,
                    percent_format,
                    date_format
                )
            elif report_type == "performance":
                self._create_performance_sheets(
                    writer,
                    data,
                    header_format,
                    number_format,
                    percent_format,
                    date_format
                )
            elif report_type == "risk":
                self._create_risk_sheets(
                    writer,
                    data,
                    header_format,
                    number_format,
                    percent_format,
                    date_format
                )
            
            # Save Excel file
            writer.close()
            
            return {
                "success": True,
                "filename": filename,
                "message": "Excel report generated successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to generate Excel report"
            }
    
    async def generate_pdf_report(self, data: Dict,
                                report_type: str) -> Dict:
        """Generate detailed PDF report with charts and analysis."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"trading_report_{report_type}_{timestamp}.pdf"
            
            # Create PDF
            pdf = FPDF()
            
            # Add title page
            self._create_pdf_title_page(pdf, report_type)
            
            # Add content based on report type
            if report_type == "portfolio":
                self._create_portfolio_pdf(pdf, data)
            elif report_type == "performance":
                self._create_performance_pdf(pdf, data)
            elif report_type == "risk":
                self._create_risk_pdf(pdf, data)
            
            # Add charts
            self._add_charts_to_pdf(pdf, data)
            
            # Add summary
            self._add_summary_to_pdf(pdf, data)
            
            # Save PDF
            pdf.output(filename)
            
            return {
                "success": True,
                "filename": filename,
                "message": "PDF report generated successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to generate PDF report"
            }
    
    def _create_portfolio_sheets(self, writer: pd.ExcelWriter,
                               data: Dict,
                               header_format,
                               number_format,
                               percent_format,
                               date_format):
        """Create portfolio-related Excel sheets."""
        # Holdings sheet
        holdings_df = pd.DataFrame(data["holdings"])
        holdings_df.to_excel(
            writer,
            sheet_name="Holdings",
            index=False,
            startrow=1
        )
        self._format_sheet(
            writer,
            "Holdings",
            holdings_df,
            header_format,
            number_format
        )
        
        # Performance sheet
        performance_df = pd.DataFrame(data["performance"])
        performance_df.to_excel(
            writer,
            sheet_name="Performance",
            index=False,
            startrow=1
        )
        self._format_sheet(
            writer,
            "Performance",
            performance_df,
            header_format,
            percent_format
        )
        
        # Transactions sheet
        transactions_df = pd.DataFrame(data["transactions"])
        transactions_df.to_excel(
            writer,
            sheet_name="Transactions",
            index=False,
            startrow=1
        )
        self._format_sheet(
            writer,
            "Transactions",
            transactions_df,
            header_format,
            date_format
        )
    
    def _create_performance_sheets(self, writer: pd.ExcelWriter,
                                 data: Dict,
                                 header_format,
                                 number_format,
                                 percent_format,
                                 date_format):
        """Create performance-related Excel sheets."""
        # Returns sheet
        returns_df = pd.DataFrame(data["returns"])
        returns_df.to_excel(
            writer,
            sheet_name="Returns",
            index=False,
            startrow=1
        )
        self._format_sheet(
            writer,
            "Returns",
            returns_df,
            header_format,
            percent_format
        )
        
        # Metrics sheet
        metrics_df = pd.DataFrame(data["metrics"])
        metrics_df.to_excel(
            writer,
            sheet_name="Metrics",
            index=False,
            startrow=1
        )
        self._format_sheet(
            writer,
            "Metrics",
            metrics_df,
            header_format,
            number_format
        )
        
        # Attribution sheet
        attribution_df = pd.DataFrame(data["attribution"])
        attribution_df.to_excel(
            writer,
            sheet_name="Attribution",
            index=False,
            startrow=1
        )
        self._format_sheet(
            writer,
            "Attribution",
            attribution_df,
            header_format,
            percent_format
        )
    
    def _create_risk_sheets(self, writer: pd.ExcelWriter,
                           data: Dict,
                           header_format,
                           number_format,
                           percent_format,
                           date_format):
        """Create risk-related Excel sheets."""
        # Risk Metrics sheet
        risk_df = pd.DataFrame(data["risk_metrics"])
        risk_df.to_excel(
            writer,
            sheet_name="Risk Metrics",
            index=False,
            startrow=1
        )
        self._format_sheet(
            writer,
            "Risk Metrics",
            risk_df,
            header_format,
            number_format
        )
        
        # Exposure sheet
        exposure_df = pd.DataFrame(data["exposure"])
        exposure_df.to_excel(
            writer,
            sheet_name="Exposure",
            index=False,
            startrow=1
        )
        self._format_sheet(
            writer,
            "Exposure",
            exposure_df,
            header_format,
            percent_format
        )
        
        # Stress Tests sheet
        stress_df = pd.DataFrame(data["stress_tests"])
        stress_df.to_excel(
            writer,
            sheet_name="Stress Tests",
            index=False,
            startrow=1
        )
        self._format_sheet(
            writer,
            "Stress Tests",
            stress_df,
            header_format,
            percent_format
        )
    
    def _format_sheet(self, writer: pd.ExcelWriter,
                     sheet_name: str,
                     df: pd.DataFrame,
                     header_format,
                     data_format):
        """Format Excel sheet with proper styling."""
        worksheet = writer.sheets[sheet_name]
        
        # Write title
        worksheet.write(0, 0, f"{sheet_name} Report", header_format)
        
        # Format headers
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(1, col_num, value, header_format)
        
        # Format data
        for row in range(len(df)):
            for col in range(len(df.columns)):
                worksheet.write(
                    row + 2,
                    col,
                    df.iloc[row, col],
                    data_format
                )
        
        # Adjust column widths
        for col_num, value in enumerate(df.columns.values):
            max_length = max(
                df[value].astype(str).apply(len).max(),
                len(value)
            )
            worksheet.set_column(col_num, col_num, max_length + 2)
    
    def _create_pdf_title_page(self, pdf: FPDF, report_type: str):
        """Create PDF report title page."""
        pdf.add_page()
        pdf.set_font("Arial", "B", 24)
        
        # Add logo
        # pdf.image("logo.png", x=10, y=10, w=30)
        
        # Add title
        pdf.cell(
            0,
            20,
            f"Trading {report_type.capitalize()} Report",
            align="C",
            ln=True
        )
        
        # Add date
        pdf.set_font("Arial", "", 12)
        pdf.cell(
            0,
            10,
            f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            align="C",
            ln=True
        )
    
    def _create_portfolio_pdf(self, pdf: FPDF, data: Dict):
        """Create portfolio section in PDF report."""
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Portfolio Overview", ln=True)
        
        # Add holdings table
        self._add_table_to_pdf(
            pdf,
            data["holdings"],
            ["Symbol", "Quantity", "Avg Price", "Current Value"]
        )
        
        # Add performance metrics
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Performance Metrics", ln=True)
        
        for metric, value in data["performance"].items():
            pdf.set_font("Arial", "", 12)
            pdf.cell(0, 10, f"{metric}: {value}", ln=True)
    
    def _create_performance_pdf(self, pdf: FPDF, data: Dict):
        """Create performance section in PDF report."""
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Performance Analysis", ln=True)
        
        # Add returns table
        self._add_table_to_pdf(
            pdf,
            data["returns"],
            ["Period", "Return", "Benchmark", "Alpha"]
        )
        
        # Add attribution analysis
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Attribution Analysis", ln=True)
        
        for factor, contribution in data["attribution"].items():
            pdf.set_font("Arial", "", 12)
            pdf.cell(0, 10, f"{factor}: {contribution}", ln=True)
    
    def _create_risk_pdf(self, pdf: FPDF, data: Dict):
        """Create risk section in PDF report."""
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Risk Analysis", ln=True)
        
        # Add risk metrics table
        self._add_table_to_pdf(
            pdf,
            data["risk_metrics"],
            ["Metric", "Value", "Limit", "Status"]
        )
        
        # Add stress test results
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Stress Test Results", ln=True)
        
        for scenario, impact in data["stress_tests"].items():
            pdf.set_font("Arial", "", 12)
            pdf.cell(0, 10, f"{scenario}: {impact}", ln=True)
    
    def _add_table_to_pdf(self, pdf: FPDF, data: Dict,
                         headers: List[str]):
        """Add formatted table to PDF."""
        pdf.set_font("Arial", "B", 12)
        
        # Calculate column width
        col_width = pdf.w / len(headers)
        row_height = 10
        
        # Add headers
        for header in headers:
            pdf.cell(col_width, row_height, header, 1)
        pdf.ln()
        
        # Add data
        pdf.set_font("Arial", "", 12)
        for row in data:
            for item in row:
                pdf.cell(col_width, row_height, str(item), 1)
            pdf.ln()
    
    def _add_charts_to_pdf(self, pdf: FPDF, data: Dict):
        """Add charts to PDF report."""
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Charts and Visualizations", ln=True)
        
        # Add charts
        # Note: Charts should be saved as images first
        # pdf.image("performance_chart.png", x=10, y=30, w=190)
        # pdf.image("risk_chart.png", x=10, y=150, w=190)
    
    def _add_summary_to_pdf(self, pdf: FPDF, data: Dict):
        """Add executive summary to PDF report."""
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Executive Summary", ln=True)
        
        pdf.set_font("Arial", "", 12)
        for key, value in data["summary"].items():
            pdf.cell(0, 10, f"{key}: {value}", ln=True)
