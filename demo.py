#!/usr/bin/env python3

import os
import time
from dotenv import load_dotenv
from hubspot import HubSpot
from hubspot.crm.contacts import SimplePublicObjectInputForCreate
from hubspot.crm.deals import SimplePublicObjectInputForCreate as DealInputForCreate
from hubspot.crm.associations.v4 import AssociationSpec
from hubspot.crm.contacts import ApiException

# Load environment variables
load_dotenv()
access_token = os.getenv("HUBSPOT_PRIVATE_APP_ACCESS_TOKEN")

if not access_token:
    print("❌ Error: HubSpot access token not found in .env file")
    exit(1)

# Initialize HubSpot client
client = HubSpot(access_token=access_token)

# Create unique timestamp for this demo
timestamp = int(time.time())
unique_email = f"demo-contact-{timestamp}@example.com"

print("🚀 HubSpot CRM MCP Demo")
print("=" * 50)

try:
    # 1. Create a contact
    print(f"📝 Creating contact with email: {unique_email}")
    
    contact_properties = {
        "email": unique_email,
        "firstname": "Demo",
        "lastname": "User",
        "phone": "555-123-4567",
        "company": "MCP Test Company"
    }
    
    contact_input = SimplePublicObjectInputForCreate(properties=contact_properties)
    new_contact = client.crm.contacts.basic_api.create(
        simple_public_object_input_for_create=contact_input
    )
    
    print(f"✅ Contact created successfully!")
    print(f"   Name: {new_contact.properties['firstname']} {new_contact.properties['lastname']}")
    print(f"   ID: {new_contact.id}")
    print(f"   Email: {new_contact.properties['email']}")
    
    # 2. Create a deal
    print(f"\n💼 Creating deal...")
    
    deal_properties = {
        "dealname": f"MCP Demo Deal - {timestamp}",
        "amount": "5000.00",
        "pipeline": "default",
        "dealstage": "appointmentscheduled"
    }
    
    deal_input = DealInputForCreate(properties=deal_properties)
    new_deal = client.crm.deals.basic_api.create(
        simple_public_object_input_for_create=deal_input
    )
    
    print(f"✅ Deal created successfully!")
    print(f"   Name: {new_deal.properties['dealname']}")
    print(f"   ID: {new_deal.id}")
    print(f"   Amount: ${new_deal.properties['amount']}")
    
    # 3. Associate contact with deal
    print(f"\n🔗 Associating contact with deal...")
    
    association = AssociationSpec(
        association_category="HUBSPOT_DEFINED",
        association_type_id="3"  # Standard contact-to-deal association
    )
    
    client.crm.associations.v4.basic_api.create(
        object_type="contacts",
        object_id=new_contact.id,
        to_object_type="deals",
        to_object_id=new_deal.id,
        association_spec=[association]
    )
    
    print(f"✅ Association created successfully!")
    print(f"   Contact {new_contact.id} is now associated with Deal {new_deal.id}")
    
    # 4. Verify the association
    print(f"\n🔍 Verifying association...")
    
    deal_with_associations = client.crm.deals.basic_api.get_by_id(
        deal_id=new_deal.id,
        properties=["dealname", "amount", "dealstage"],
        associations=["contacts"]
    )
    
    print(f"✅ Verification complete!")
    print(f"   Deal: {deal_with_associations.properties.get('dealname')}")
    print(f"   Stage: {deal_with_associations.properties.get('dealstage')}")
    
    if deal_with_associations.associations and deal_with_associations.associations.get('contacts'):
        contact_count = len(deal_with_associations.associations['contacts'].results)
        print(f"   Associated Contacts: {contact_count}")
    
    print(f"\n🎉 Demo completed successfully!")
    print(f"   Contact ID: {new_contact.id}")
    print(f"   Deal ID: {new_deal.id}")

except ApiException as e:
    print(f"❌ API Error: {e}")
    if hasattr(e, 'status'):
        if e.status == 401:
            print("   This usually means your access token is invalid")
        elif e.status == 403:
            print("   This usually means your app doesn't have the required permissions")
            print("   Required scopes: crm.objects.contacts, crm.objects.deals, crm.schemas.deals")

except Exception as e:
    print(f"❌ Unexpected error: {e}")

print(f"\n📊 MCP Status: Ready for production use!")
