"""Alert email functions"""

from datetime import datetime
from typing import Any, Dict, Optional

from airflow.models import Variable
from airflow.utils.email import send_email

ALERT_EMAIL = Variable.get("email_to_send_alert")


def send_status_email(
    etl_name: str, success: bool = True, context: Optional[Dict[str, Any]] = None
) -> None:
    """Sends an email notification indicating the success or failure of the ETL process.

    This function sends an email notification based on the status of the ETL process. If the ETL
    process failed, the email will include error information extracted from the context provided
    by Airflow.

    Args:
        etl_name (str): The name of the ETL process.
        success (bool): Indicates whether the ETL process was successful or not. Defaults to True.
        context (Optional[Dict[str, Any]]): Airflow context dictionary containing task and DAG info.
            If not provided and `success` is False, the email will have limited information.

    Returns:
        None: This function does not return any value.
    """
    current_timestamp_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if success:
        subject = f"✅ ETL {etl_name}: Success"
        body = f"""
        <p>The ETL process for {etl_name} has completed successfully at {current_timestamp_at}.</p>
        <p>No further actions are required.</p>
        """
    else:
        subject = f"❌ ETL {etl_name} Failure"

        dag_id = context["dag"].dag_id if context and context.get("dag") else "Unknown"
        task_id = (
            context["task_instance"].task_id
            if context and context.get("task_instance")
            else "Unknown"
        )
        execution_date = (
            context["execution_date"].strftime("%Y-%m-%d %H:%M:%S")
            if context and context.get("execution_date")
            else current_timestamp_at
        )
        log_url = (
            context["task_instance"].log_url
            if context and context.get("task_instance")
            else "Unavailable"
        )
        error = (
            context.get("exception", "No error message available.")
            if context
            else "No error message available."
        )

        body = f"""
        <p>The ETL process has failed. Check details below:</p>
        <p><b>Dag:</b> {dag_id}</p>
        <p><b>Task:</b> {task_id}</p>
        <p><b>Execution Date:</b> {execution_date}</p>
        <p><b>Error:</b> {error}</p>
        <p>For more details, please check the <a href="{log_url}">logs</a>.</p>
        """

    send_email(ALERT_EMAIL, subject, body)


def on_failure_callback(context: Dict[str, Any]) -> None:
    """Callback function to be executed on task failure.

    This function is intended to be used as a callback in Airflow tasks. It sends an email with
    error information extracted from the provided context when the task fails.

    Args:
        context (Dict[str, Any]): Airflow context dictionary containing task and DAG info. This
            context is used to extract information about the failed task and include it in the
            failure notification email.

    Returns:
        None: This function does not return any value.
    """
    send_status_email(etl_name="", success=False, context=context)
