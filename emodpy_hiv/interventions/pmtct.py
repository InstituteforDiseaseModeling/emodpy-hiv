from emod_api import schema_to_class as s2c
from emod_api.interventions import utils
import json

def new_intervention( camp, efficacy=1.0 ):
    """
    PMTCT intervention wrapper. Just the intervention. No configuration yet.
    """
    intervention = s2c.get_class_with_defaults( "PMTCT", camp.schema_path )
    intervention.Efficacy = efficacy
    return intervention

def new_intervention_event( 
        camp, 
        start_day=1, 
        coverage=1.0, 
        node_ids=None
    ):
    """
    PMTCT intervention as complete (scheduled) event.
    """
    iv = new_intervention( camp )

    # Coordinator
    coordinator = s2c.get_class_with_defaults( "StandardEventCoordinator", camp.schema_path )
    coordinator.Intervention_Config = iv
    coordinator.Demographic_Coverage = coverage

    # Event
    event = s2c.get_class_with_defaults( "CampaignEvent", camp.schema_path ) 
    event.Event_Coordinator_Config = coordinator
    event.Start_Day = float(start_day)
    event.Nodeset_Config = utils.do_nodes( camp.schema_path, node_ids )
    from . import utils as hiv_utils
    hiv_utils.declutter( event )

    return event

def new_intervention_as_file( camp, start_day, filename=None ):
    import emod_api.campaign as camp
    camp.add( new_intervention_event( camp, start_day ), first=True )
    if filename is None:
        filename = "PMTCT.json"
    camp.save( filename )
    return filename
