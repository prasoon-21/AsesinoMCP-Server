import random
from fastmcp import FastMCP

#creating a fastmcp instance
mcp=FastMCP(name="First Server")

@mcp.tool
def roll_dice(n_dice: int = 1)->list[int]:
    """Roll n_dice 6-sided dice and return the results."""
    return [random.randint(1, 6) for i in range(n_dice)]

@mcp.tool
def add_numbers(a:float, b:float)->float:
    """Add two number"""
    return a+b

@mcp.tool
def sub_numbers(a:float, b:float)->float:
    """Subs two numbers"""
    return a-b

@mcp.tool
def multiply_numbers(a:float, b:float)->float:
    """Multiplying two number"""
    return a*b

@mcp.tool
def divide_numbers(a:float, b:float)->float:
    """Dividing the first number with the other one"""
    return a/b

@mcp.tool
def module_numbers(a:float, b:float)->float:
    """Finding the module of numbers"""
    return a%b

