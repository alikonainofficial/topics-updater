import os
import argparse
import ast
import logging
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client, Client

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Load environment variables from .env file
load_dotenv()


def main(csv_file, checkpoint_file, table, column, supabase_url, supabase_key):
    # Create Supabase client
    supabase: Client = create_client(supabase_url, supabase_key)

    # Read the CSV file
    df = pd.read_csv(csv_file)

    # Function to read the last processed ID from the checkpoint file
    def read_last_processed_id():
        if os.path.exists(checkpoint_file):
            with open(checkpoint_file, "r") as file:
                last_id = file.read().strip()
                return last_id if last_id else None
        return None

    # Function to update the checkpoint file with the current ID
    def update_checkpoint(book_id):
        with open(checkpoint_file, "w") as file:
            file.write(str(book_id))

    # Get the last processed ID
    last_processed_id = read_last_processed_id()

    # If there's a last processed ID, filter the dataframe starting from the next entry
    if last_processed_id:
        try:
            # Find the index of the last processed ID in the DataFrame
            last_processed_index = df.index[df["id"] == last_processed_id].tolist()
            if last_processed_index:
                # Resume from the next row
                df = df.iloc[last_processed_index[0] + 1 :]
        except Exception as e:
            logging.error(
                f"An error occurred while trying to filter the DataFrame: {e}"
            )
            return

    # Update the database
    for _, row in df.iterrows():
        row_id = row["id"]
        topics_str = row["topics_list"]

        # Convert the string representation of the list into an actual Python list
        try:
            topics = ast.literal_eval(topics_str)
            if not isinstance(topics, list):
                raise ValueError("The topics_list is not a valid list.")
        except (ValueError, SyntaxError) as e:
            logging.warning(
                f"Skipping row with id {row_id}: Invalid list format. Error: {e}"
            )
            continue

        # Update the topics column in the categories table
        try:
            response = (
                supabase.table(table)
                .update({column: topics})
                .eq("id", row_id)
                .execute()
            )

            # Check if the update was successful
            if response.data:
                logging.info(f"Successfully updated topics for id {row_id}")
                # Update the checkpoint file with the current successfully processed ID
                update_checkpoint(row_id)
            elif response.error:
                logging.error(
                    f"Failed to update topics for id {row_id}. Error: {response.error}"
                )
            else:
                logging.warning(f"Unexpected response for id {row_id}: {response}")
        except Exception as e:
            logging.error(f"An error occurred: {e}")


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Update topics in categories or books_metadata table, through a CSV file"
    )
    parser.add_argument(
        "csv_file", help="Path to the CSV file containing topics per category"
    )
    parser.add_argument("checkpoint_file", help="Path to the checkpoint file")
    parser.add_argument(
        "table",
        choices=["categories", "books_metadata"],
        help="The table to update (categories or books_metadata)",
    )
    parser.add_argument(
        "column",
        choices=["topics", "ai_topics"],
        help="The column to update (topics or ai_topics)",
    )
    parser.add_argument(
        "--supabase_url", default=os.getenv("SUPABASE_URL"), help="Supabase URL"
    )
    parser.add_argument(
        "--supabase_key", default=os.getenv("SUPABASE_KEY"), help="Supabase API Key"
    )

    args = parser.parse_args()

    # Run the main function with arguments
    main(
        args.csv_file,
        args.checkpoint_file,
        args.table,
        args.column,
        args.supabase_url,
        args.supabase_key,
    )
