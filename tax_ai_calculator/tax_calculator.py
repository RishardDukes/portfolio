"""
Tax Calculator Module
Handles all tax calculation logic
"""

class TaxCalculator:
    """Main tax calculation engine"""
    
    def __init__(self, tax_year=2024):
        self.tax_year = tax_year
        self.standard_deduction_single = 13850
        self.standard_deduction_married = 27700
        self.tax_brackets = self._get_tax_brackets()
    
    def _get_tax_brackets(self):
        """Returns 2024 federal tax brackets for single filers"""
        return [
            (11000, 0.10),
            (44725, 0.12),
            (95375, 0.22),
            (182100, 0.24),
            (231250, 0.32),
            (578125, 0.35),
            (float('inf'), 0.37)
        ]
    
    def calculate_taxable_income(self, gross_income, deductions=0, standard_deduction=True):
        """Calculate taxable income after deductions"""
        if standard_deduction:
            deductions = self.standard_deduction_single
        
        taxable_income = max(0, gross_income - deductions)
        return taxable_income
    
    def calculate_federal_tax(self, taxable_income):
        """Calculate federal income tax based on brackets"""
        if taxable_income <= 0:
            return 0
        
        tax = 0
        previous_limit = 0
        
        for limit, rate in self.tax_brackets:
            if taxable_income <= previous_limit:
                break
            
            amount_in_bracket = min(taxable_income, limit) - previous_limit
            tax += amount_in_bracket * rate
            previous_limit = limit
        
        return round(tax, 2)
    
    def calculate_total_tax(self, gross_income, deductions=0, credits=0, standard_deduction=True):
        """Calculate total tax liability"""
        taxable_income = self.calculate_taxable_income(gross_income, deductions, standard_deduction)
        federal_tax = self.calculate_federal_tax(taxable_income)
        
        # Apply tax credits
        total_tax = max(0, federal_tax - credits)
        return round(total_tax, 2)
    
    def calculate_refund(self, gross_income, total_withheld, deductions=0, credits=0):
        """Calculate refund or amount owed"""
        tax_owed = self.calculate_total_tax(gross_income, deductions, credits)
        refund = total_withheld - tax_owed
        
        return {
            'tax_owed': tax_owed,
            'total_withheld': total_withheld,
            'refund' if refund >= 0 else 'amount_owed': abs(refund)
        }


if __name__ == "__main__":
    calc = TaxCalculator()
    
    # Example usage
    gross = 55000
    withheld = 8000
    deductions = 2000
    credits = 500
    
    result = calc.calculate_refund(gross, withheld, deductions, credits)
    print(f"Calculation for ${gross:,} income:")
    print(f"Tax owed: ${result['tax_owed']:,.2f}")
    print(f"Withheld: ${result['total_withheld']:,.2f}")
    print(result)
