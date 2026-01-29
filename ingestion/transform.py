class Transform:
    def __init__(self, table_df, features):
        self.table_df = table_df
        self.features = features

    def clean_data(self):
        """Remove noise, empty rows, broken lines"""

    def normalize_data(self):
        """Standardize column names, values, formats"""

    def symbol_to_logic(self):
        """Convert bullets/dots into Yes/No"""

    def keyword_mapping(self):
        """Force features into correct categories"""

    def final_data_model(self):
        """Create final DataFrame schema"""

    def validate_data(self):
        """Identify missing or invalid fields"""
