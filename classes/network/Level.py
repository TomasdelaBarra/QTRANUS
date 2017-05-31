
def enum(**enums):
    return type('Enum', (), enums)

Level = enum(Total = 1, Operators = 2, Routes = 3)