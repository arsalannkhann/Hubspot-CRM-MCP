import os
import time
from dotenv import load_dotenv
from hubspot import HubSpot
from hubspot.crm.contacts import SimplePublicObjectInputForCreate, ApiException as ContactsApiException
from hubspot.crm.deals import SimplePublicObjectInputForCreate as DealInputForCreate
from hubspot.crm.associations import BatchInputPublicAssociation, PublicAssociation

# --- Configuration and Initialization ---

def setup_hubspot_client():
    """
    Loads credentials from a .env file and initializes the HubSpot API client.
    For production, it's recommended to use a Private App access token stored securely.
    """
    load_dotenv()
    access_token = os.getenv("HUBSPOT_PRIVATE_APP_ACCESS_TOKEN")

    if not access_token:
        print("Error: HubSpot access token not found. Please set HUBSPOT_PRIVATE_APP_ACCESS_TOKEN in your .env file.")
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
        print(f"✅ Contact created: {api_response.properties['firstname']} (ID: {api_response.id})")
        return api_response
    except ContactsApiException as e:
        handle_api_error(e)
        return None

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
        print(f"✅ Deal created: {api_response.properties['dealname']} (ID: {api_response.id})")
        return api_response
    except Exception as e:
        handle_api_error(e)
        return None

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
            from_object_type="contact",
            to_object_type="deal",
            batch_input_public_association=association_input
        )
        print(f"🔗 Associated {from_object_type} {from_object_id} → {to_object_type} {to_object_id}")
        return result
    except Exception as e:
        handle_api_error(e)
        return None

def get_deal_with_associations(api_client, deal_id):
    try:
        deal = api_client.crm.deals.basic_api.get_by_id(
            deal_id,
            properties=["dealname", "amount", "dealstage"],
            associations=["contacts", "companies"]
        )
        return deal
    except Exception as e:
        handle_api_error(e)
        return None

# --- Utility ---

def handle_api_error(e):
    if hasattr(e, 'status') and e.status == 429:
        print("⚠️ HubSpot API rate limit exceeded. Please retry later.")
    else:
        print(f"❌ HubSpot API error: {e}")

# --- Main ---

if __name__ == "__main__":
    print("🚀 HubSpot CRM MCP - Starting Demo")
    print("=" * 50)
    
    client = setup_hubspot_client()

    if client:
        # Generate unique email to avoid conflicts
        timestamp = int(time.time())
        unique_email = f"mcp-demo-{timestamp}@example.com"
        
        new_contact = create_contact(
            client,
            email=unique_email,
            firstname="MCP Demo",
            lastname="Contact",
            phone="555-123-4567"
        )

        if new_contact:
            new_deal = create_deal(
                client,
                deal_name=f"MCP Demo Deal - {timestamp}",
                amount="10000.00",
                pipeline="default",
                deal_stage="appointmentscheduled"
            )

            if new_deal:
                associate_records(
                    client,
                    from_object_type="contacts",
                    from_object_id=new_contact.id,
                    to_object_type="deals",
                    to_object_id=new_deal.id
                )

                deal = get_deal_with_associations(client, new_deal.id)
                if deal:
                    print("\n--- Deal Summary ---")
                    print(f"Name: {deal.properties.get('dealname')}")
                    print(f"Amount: ${deal.properties.get('amount')}")
                    print(f"Stage: {deal.properties.get('dealstage')}")
                    if deal.associations and deal.associations.get("contacts"):
                        contact_count = len(deal.associations['contacts'].results)
                        print(f"Contacts linked: {contact_count}")
                    
                    print("\n🎉 HubSpot CRM MCP Demo completed successfully!")
                    print(f"Contact ID: {new_contact.id}")
                    print(f"Deal ID: {new_deal.id}")
                    print("📊 MCP Status: Ready for production use!")
                else:
                    print("⚠️ Could not retrieve deal summary")
            else:
                print("❌ Failed to create deal")
        else:
            print("❌ Failed to create contact")
    else:
        print("❌ Failed to initialize HubSpot client")
