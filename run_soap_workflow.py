import asyncio
import logging
from termcolor import colored  # For colored print statements

from aurite import Aurite
from aurite.config.config_models import AgentConfig, LLMConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """
    A simple example demonstrating how to initialize Aurite, dynamically register a custom workflow,
    and run it for SOAP note generation.
    """
    # Initialize the main Aurite application object.
    # This will load configurations based on `aurite_config.json` or environment variables.
    # Load environment variables from a .env file if it exists
    from dotenv import load_dotenv

    load_dotenv()

    aurite = Aurite()

    try:
        await aurite.initialize()

        # --- Dynamic Custom Workflow Registration Example ---
        # Try to dynamically register the custom workflow
        try:
            # Import the workflow class
            from example_custom_workflows.soap_note_workflow import SoapNoteWorkflow
            
            # Try to register the workflow if there's a method for it
            if hasattr(aurite, 'register_custom_workflow'):
                await aurite.register_custom_workflow(
                    name="soap-note-workflow",
                    workflow_class=SoapNoteWorkflow,
                    description="A workflow for generating SOAP notes from audio recordings."
                )
                print(colored("Custom workflow registered dynamically", "green"))
            else:
                print(colored("Dynamic workflow registration not available, using config file", "yellow"))
                
        except Exception as reg_error:
            logger.warning(f"Dynamic registration failed: {reg_error}")
            print(colored("Using config file workflow registration", "yellow"))
        # --- End of Dynamic Registration Example ---

        # Define the input for the workflow
        mp3_file = "Record_test.mp3"  # 可根据实际情况修改
        workflow_name = "soap-note-workflow"

        # Print workflow start information
        print(colored(f"\n--- Running Custom Workflow: {workflow_name} ---", "yellow", attrs=["bold"]))
        print(colored(f"Input audio file: {mp3_file}", "blue"))

        # Try different workflow execution methods
        workflow_result = None
        
        # Method 1: Try run_custom_workflow if it exists
        if hasattr(aurite, 'run_custom_workflow'):
            try:
                workflow_result = await aurite.run_custom_workflow(
                    workflow_name=workflow_name,
                    initial_input={"mp3_file": mp3_file}
                )
                print(colored("Used run_custom_workflow method", "green"))
            except Exception as e:
                logger.warning(f"run_custom_workflow failed: {e}")
        
        # Method 2: Fallback to run_workflow
        if workflow_result is None:
            try:
                workflow_result = await aurite.run_workflow(
                    workflow_name=workflow_name,
                    initial_input={"mp3_file": mp3_file}
                )
                print(colored("Used run_workflow method", "green"))
            except Exception as e:
                logger.error(f"run_workflow also failed: {e}")
                raise

        # Process the workflow result
        result_dict = vars(workflow_result) if not isinstance(workflow_result, dict) else workflow_result
        
        # Print the workflow's response in a colored format for better visibility.
        if result_dict.get("status") == "completed":
            print(colored("\n--- SOAP Note Generated Successfully ---", "green", attrs=["bold"]))
            print(colored(f"\nSOAP Note Content:", "cyan"))
            print("=" * 60)
            print(result_dict["soap_note"])
            print("=" * 60)
            print(colored(f"\nSOAP note saved to: {result_dict['soap_note_file']}", "green"))
        else:
            print(colored(f"\nWorkflow failed: {result_dict.get('error')}", "red"))

    except Exception as e:
        logger.error(f"An error occurred during workflow execution: {e}", exc_info=True)
    finally:
        await aurite.shutdown()
        logger.info("Aurite shutdown complete.")


if __name__ == "__main__":
    # Run the asynchronous main function.
    asyncio.run(main())
