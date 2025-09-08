import os
from dotenv import load_dotenv
from hubspot import HubSpot
from hubspot.crm.contacts import SimplePublicObjectInputForCreate, ApiException as ContactsApiException
from hubspot.crm.deals import SimplePublicObjectInputForCreate as DealInputForCreate
from hubspot.crm.associations import BatchInputPublicAssociation, PublicAssociation
from mcp.server import Server
from typing import Dict

# --- Configuration and Initialization ---

def setup_hubspot_client():
    """
    Loads credentials from a .env file and initializes the HubSpot API client.
    For production, it's recommended to use a Private App access token stored securely.
    """
    load_dotenv()
    access_token = os.getenv("HUBSPOT_PRIVATE_APP_ACCESS_TOKEN")

    if not access_token:
        return None

    # Initialize the HubSpot client with access token
    return HubSpot(access_token=access_token)

# --- Core CRM Functions ---

def create_contact(api_client, email, firstname, lastname, phone):
    try:
        properties = {
            "email": email,
            "firstname": firstname,
            "lastname": lastname,
            "phone": phone
        }
        contact_input = SimplePublicObjectInputForCreate(properties=properties)

        api_response = api_client.crm.contacts.basic_api.create(
            simple_public_object_input_for_create=contact_input
        )
        return api_response
    except ContactsApiException as e:
        return {"error": str(e)}

def create_deal(api_client, deal_name, amount, pipeline, deal_stage):
    try:
        properties = {
            "dealname": deal_name,
            "amount": amount,
            "pipeline": pipeline,
            "dealstage": deal_stage
        }
        deal_input = DealInputForCreate(properties=properties)

        api_response = api_client.crm.deals.basic_api.create(
            simple_public_object_input_for_create=deal_input
        )
        return api_response
    except Exception as e:
        return {"error": str(e)}

def associate_records(api_client, from_object_type, from_object_id, to_object_type, to_object_id):
    """Create association between two CRM records using the legacy v3 API (more reliable)"""
    try:
        association_input = BatchInputPublicAssociation(
            inputs=[
                PublicAssociation(
                    _from={"id": from_object_id},
                    to={"id": to_object_id},
                    type="contact_to_deal"  # Standard association type
                )
            ]
        )
        
        result = api_client.crm.associations.batch_api.create(
            from_object_type=from_object_type,
            to_object_type=to_object_type,
            batch_input_public_association=association_input
        )
        return {"success": True}
    except Exception as e:
        return {"error": str(e)}

def get_deal_with_associations(api_client, deal_id):
    try:
        deal = api_client.crm.deals.basic_api.get_by_id(
            deal_id,
            properties=["dealname", "amount", "dealstage"],
            associations=["contacts", "companies"]
        )
        return deal
    except Exception as e:
        return {"error": str(e)}

# --- MCP Server and Tools ---

hubspot_server = Server("hubspot-crm")

@hubspot_server.tool()
def create_contact_tool(email: str, firstname: str, lastname: str, phone: str) -> Dict:
    api_client = setup_hubspot_client()
    if not api_client:
        return {"error": "HubSpot client initialization failed"}
    contact = create_contact(api_client, email, firstname, lastname, phone)
    if isinstance(contact, dict) and "error" in contact:
        return contact
    return {"id": contact.id, "email": contact.properties.get("email")}

@hubspot_server.tool()
def create_deal_tool(deal_name: str, amount: str, pipeline: str, deal_stage: str) -> Dict:
    api_client = setup_hubspot_client()
    if not api_client:
        return {"error": "HubSpot client initialization failed"}
    deal = create_deal(api_client, deal_name, amount, pipeline, deal_stage)
    if isinstance(deal, dict) and "error" in deal:
        return deal
    return {"id": deal.id, "dealname": deal.properties.get("dealname")}

@hubspot_server.tool()
def associate_contact_deal(from_object_type: str, from_object_id: str, to_object_type: str, to_object_id: str) -> Dict:
    api_client = setup_hubspot_client()
    if not api_client:
        return {"error": "HubSpot client initialization failed"}
    result = associate_records(api_client, from_object_type, from_object_id, to_object_type, to_object_id)
    return result

@hubspot_server.tool()
def get_deal_summary(deal_id: str) -> Dict:
    api_client = setup_hubspot_client()
    if not api_client:
        return {"error": "HubSpot client initialization failed"}
    deal = get_deal_with_associations(api_client, deal_id)
    if isinstance(deal, dict) and "error" in deal:
        return deal
    contact_count = 0
    if deal.associations and deal.associations.get("contacts"):
        contact_count = len(deal.associations["contacts"].results)
    return {
        "dealname": deal.properties.get("dealname"),
        "amount": deal.properties.get("amount"),
        "dealstage": deal.properties.get("dealstage"),
        "contact_count": contact_count
    }

if __name__ == "__main__":
    hubspot_server.run()
