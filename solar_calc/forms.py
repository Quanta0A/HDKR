from django import forms
from datetime import datetime

class RadiationForm(forms.Form):
    MODE_CHOICES = [
        ('single_day', 'Single Day'),
        ('full_month', 'Full Month'),
        ('12_month', '12 Months'),  # Updated choice for 12 months
        ('365_days', '365 Days')     # Updated choice for 365 days
    ]
    UNIT_CHOICES = [
        ('MJ', 'MJ/m²/day'),
        ('W', 'W/m²')
    ]

    latitude = forms.FloatField(
        label='Latitude (°)',
        widget=forms.NumberInput(attrs={'step': '0.01'})
    )

    tilt = forms.FloatField(
        label='Tilt Angle (°)',
        widget=forms.NumberInput(attrs={'step': '0.01'})
    )

    date = forms.DateField(
        required=False,
        label='Date (for Single Day)',
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    month = forms.ChoiceField(
        required=False,
        label='Month (for Full Month)',
        choices=[(str(i), month) for i, month in enumerate([
            "January", "February", "March", "April", "May", "June", "July",
            "August", "September", "October", "November", "December"], 1)]
    )
    year = forms.IntegerField(
    required=False,
    label='Year',
    initial=datetime.now().year,
    widget=forms.NumberInput(attrs={'min': 1900, 'max': 2100}),
    help_text='Year for which the radiation is being calculated'
)


    ghi = forms.CharField(
        label='GHI Value(s)',
        help_text="For full month, enter comma-separated values."
    )

    sunshine_hours = forms.CharField(
        required=False,
        label='Sunshine Hours',
        help_text="Only required if GHI is in W/m²"
    )

    ghi_unit = forms.ChoiceField(
        label='GHI Unit',
        choices=UNIT_CHOICES
    )

    mode = forms.ChoiceField(
        label='Calculation Mode',
        choices=MODE_CHOICES
    )

    csv_file = forms.FileField(
        required=False,
        label='Upload CSV (optional)',
        help_text="CSV with GHI and optional Sunshine columns"
    )