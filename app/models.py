# models.py

class FuelEntry:
    """
    Represents a single fuel entry for a vehicle.

    Attributes:
        date (str): The date of the fuel entry in YYYY-MM-DD format.
        liters (float): The amount of fuel filled in liters.
        price_per_liter (float): The price paid per liter of fuel.
        distance (float): Distance driven since last refuel, in kilometers.
        notes (str): Optional notes about the entry.
    """

    def __init__(self, date, liters, price_per_liter, distance, notes=""):
        """
        Initializes a new FuelEntry instance.

        Args:
            date (str): Date of the entry (YYYY-MM-DD).
            liters (float): Liters of fuel filled.
            price_per_liter (float): Price per liter.
            distance (float): Distance driven since last refuel (in km).
            notes (str, optional): Additional notes. Defaults to "".
        """
        self.date = date
        self.liters = liters
        self.price_per_liter = price_per_liter
        self.distance = distance
        self.notes = notes
        
    @property
    def l_per_km(self) -> float:
        """
        Calculates the fuel efficiency in Liters per Kilometer (L/km).
        This is necessary for unit testing the model.
        """
        if self.distance <= 0:
            return 0.0
        
        # Formula: Liters / Distance in km
        efficiency = self.liters / self.distance
        # Using 6 decimal places for precision in L/km
        return round(efficiency, 6)

    @property
    def total_cost(self):
        """
        Calculates the total cost of the fuel entry.

        Returns:
            float: Total cost (liters × price_per_liter), rounded to 2 decimal places.
        """
        return round(self.liters * self.price_per_liter, 2)

    @property
    def fuel_consumption(self):
        """
        Calculates fuel consumption in liters per km.
        """
        if self.distance == 0:
            return 0.0
        return round(self.liters / self.distance, 4)
