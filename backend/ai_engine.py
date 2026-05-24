import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process

# Import the specific tool for reading our policy file
from crewai_tools import FileReadTool

# Load the API keys from the .env file
load_dotenv()

# Define our model constant
llm_model = os.getenv("AI_MODEL",'openrouter/meta-llama/llama-3.3-70b-instruct:nitro')
if os.getenv("USE_GROQ") == "1":
    llm_model = 'groq/groq/compound'

POLICY_PATH = 'company_policy.txt'

def evaluate_inventory(item_dict, sales_list):
    """
    Takes the catalog data and sales history, runs the AI debate,
    consults the company policy (RAG), and returns a suggested reorder quantity.
    """
    
    # Initialize the RAG Tool pointing exactly to our new document
    policy_tool = FileReadTool(file_path=POLICY_PATH)
    
    #Define the Agents
    forecaster = Agent(
        role='Demand Forecaster',
        goal='Analyze 90-day sales history and predict required stock for the next 30 days.',
        backstory='You are a veteran supply chain analyst who spots trends in time-series data.',
        verbose=True,
        llm=llm_model,
        allow_delegation=False
    )

    budget_controller = Agent(
        role='Budget Controller',
        goal='Evaluate the financial viability of stock orders based on unit price and max capacity.',
        backstory='You are a strict financial officer who prevents overspending and warehouse overflow.',
        verbose=True,
        llm=llm_model,
        allow_delegation=False
    )

    manager = Agent(
        role='Supply Chain Manager',
        goal='Review the forecaster and budget reports, then consult the company policy to make the final executive decision on exactly how many units to reorder.',
        backstory='You are the final decision-maker. You ALWAYS read the company policy document before finalizing any numbers to ensure strict compliance.',
        verbose=True,
        llm=llm_model,
        allow_delegation=False,
        tools=[policy_tool] #hand the tool specifically to the Manager
    )

    #Define the Tasks
    analyze_demand = Task(
        description=f"Analyze the following 90-day sales history for {item_dict['Product_Name']}: {sales_list}. Calculate the average daily sales and project the demand for the next 30 days.",
        expected_output="A short report detailing the daily average sales and the projected 30-day demand.",
        agent=forecaster
    )

    evaluate_finances = Task(
        description=f"Review the demand projection. The item costs ${item_dict['Unit_Price']} per unit. The warehouse max capacity for this item is {item_dict['Max_Capacity']} units. Current stock is {item_dict['Stock_Quantity']}. Calculate the cost of the proposed order and warn if it exceeds capacity.",
        expected_output="A financial summary approving or modifying the projected order based on cost and capacity limits.",
        agent=budget_controller
    )

    final_decision = Task(
        description=f"""Review the financial summary. 
        The supplier for this specific item is: {item_dict.get('Supplier_Name', 'Unknown')}.
        
        You MUST use your FileReadTool to read the company policy document. 
        Cross-reference the item details and the supplier name against the policy rules (like perishable limits, financial caps, or supplier MOQs).
        
        CRITICAL MATH REQUIREMENT: Before determining the final number, you must explicitly calculate:
        1. The exact capacity limit based on the policy rules.
        2. The sum of the current stock ({item_dict['Stock_Quantity']}) plus your proposed order.
        3. Verify that this sum is strictly less than or equal to the capacity limit.

        When evaluating the policy, you MUST process Rule 1 using this exact sequence:
        1. Identify the item's category.
        2. Check if the category is EXACTLY 'Fruits & Vegetables', 'Dairy', 'Seafood', or 'Bakery'.
        3. If NO: Explicitly write "Rule 1 does not apply to [Category]" and immediately move to Rule 2 without doing any math.
        4. If YES: Calculate the 40% maximum capacity limit.

        TONE AND FORMATTING FOR REASONING LOG:
        You must write the `reasoning_log` exactly like a human Senior Supply Chain Manager writing a quick Slack message to a colleague. 
        1. DO NOT list out "Rule 1", "Rule 2", or "Rule 3".
        2. DO NOT mention rules that did not apply to the item.
        3. Write a fluid, natural 1-to-2 sentence summary focusing ONLY on why the final quantity was chosen.
        Mention that it was the forcasted quantity by the forcast agent.

        BAD EXAMPLE: "Rule 1 does not apply. Rule 2 is satisfied as the cost is $45. Rule 3 does not apply. Order of 30 approved."
        GOOD EXAMPLE: "Approved 30 units of Bread Flour. The total cost is comfortably under our $250 budget limit and leaves plenty of warehouse space."
        Determine the final, exact integer quantity of units to reorder. 
        Output ONLY a JSON string containing two keys: 'suggested_order_quantity' (an integer) and 'reasoning_log' (a brief explanation string detailing exactly which policy rules you applied).""",
        expected_output="A strictly formatted JSON string with the final order quantity and a reasoning log that explicitly mentions the policy.",
        agent=manager
    )

    #Assemble and Run the Crew
    replenishment_crew = Crew(
        agents=[forecaster, budget_controller, manager],
        tasks=[analyze_demand, evaluate_finances, final_decision],
        process=Process.sequential
    )

    # Kick off the debate
    result = replenishment_crew.kickoff()
    
    return result

def review_basket_compliance(basket_items):
    """
    Takes a list of items, calculates the total cost, and uses RAG to ensure 
    the basket obeys the financial policy. Auto-adjusts quantities if over budget.
    """
    policy_tool = FileReadTool(file_path=POLICY_PATH)
    
    manager = Agent(
        role='Executive Supply Chain Manager',
        goal='Review and automatically optimize a proposed cart of inventory orders to strictly comply with company policy.',
        backstory='You are the final executive decision-maker. You ALWAYS read the company policy document. If an order exceeds financial limits, you automatically reduce item quantities (starting with the most expensive total line items) to the maximum allowable amount to ensure compliance.',
        verbose=True,
        llm=llm_model,
        allow_delegation=False,
        tools=[policy_tool]
    )

    review_task = Task(
        description=f"""Review the following shopping basket of proposed orders:
        {basket_items}
        
        You MUST use your FileReadTool to read the company policy document. 
        
        CRITICAL INSTRUCTIONS:
        1. Calculate the total cost of the entire basket (sum of 'quantity' * 'unit_price' for all items).
        2. Cross-reference this total against the financial cap rule in the policy.
        3. If the total exceeds the cap, you MUST reduce the 'quantity' of items until the overall basket total is strictly under the cap.
        
        Output ONLY a JSON string containing exactly two keys: 
        - 'updated_basket': A list of objects containing the 'sku', 'name', 'unit_price', and your new, optimized 'quantity'.
        - 'reasoning_log': A brief explanation detailing the exact math, which specific item quantities you reduced, and the policy rule applied.
        """,
        expected_output="A strictly formatted JSON string with 'updated_basket' and 'reasoning_log'.",
        agent=manager
    )

    basket_crew = Crew(
        agents=[manager],
        tasks=[review_task],
        process=Process.sequential
    )

    return basket_crew.kickoff()