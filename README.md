# Column Updater

This script reads a CSV file and updates specific columns in a Supabase table (`categories` or `books_metadata`) based on the data in the CSV. It uses a checkpointing system to resume processing from the last successfully updated record, ensuring that updates are applied incrementally without reprocessing already updated records.

## Features

- **CSV Input**: Reads a CSV file where each row contains the data to be updated.
- **Checkpointing**: Uses a checkpoint file to store the ID of the last successfully updated record, allowing the script to resume from where it left off.
- **Error Handling**: Logs and skips invalid rows where the data is not formatted correctly as a list.
- **Supabase Integration**: Updates data in a Supabase table (`categories` or `books_metadata`).
- **Logging**: Provides detailed logs of the script’s progress, including errors and successful updates.

## Prerequisites

- **Python 3.x**
- Required Python libraries (install using pip):

  ```bash
  pip install pandas python-dotenv supabase
  ```

  • Supabase Account: You need a Supabase project with a valid API key and table(s) (categories or books_metadata) that you want to update.

## Environment Variables

Create a .env file in the root of your project with the following variables:

```
SUPABASE_URL=<your_supabase_url>
SUPABASE_KEY=<your_supabase_api_key>
```

These values are used by the script to connect to Supabase. Alternatively, they can be passed via command line arguments.

## Usage

```bash
python3 topics_categories_updater.py <csv_file> <checkpoint_file> <table> <column> [--supabase_url SUPABASE_URL] [--supabase_key SUPABASE_KEY]
```

## Arguments

    • csv_file: The path to the CSV file containing the data to be updated. It should have columns named id and data list.
    • checkpoint_file: The path to a file where the script will store the ID of the last successfully processed row. This allows the script to resume from where it left off.
    • table: The table in Supabase to update. Choices are categories or books_metadata.
    • column: The column to update in the table. Choices are topics, ai_topics or ai_categories.
    • --supabase_url: (Optional) The URL of your Supabase instance. Defaults to the value from the .env file.
    • --supabase_key: (Optional) The API key for your Supabase instance. Defaults to the value from the .env file.

## Example

```bash
python3 topics_categories_updater.py sample_input.csv checkpoint.txt categories topics --supabase_url "https://your-supabase-url" --supabase_key "your-api-key"
```

This will update the data column in the categories table using the data from sample_input.csv. The script will resume from the last processed row if a checkpoint file exists.

## Checkpointing

The checkpoint file is a simple text file that contains the id of the last successfully processed row. If the script fails or is interrupted, it will resume processing from the row after the last recorded id in this file.

## CSV Format

The CSV file should contain at least two columns:

    • id: The unique identifier for the record.
    • topics_list or categories_list: A string representation of a list (e.g., ["topic1", "topic2"] or ["category1", "category2"]). This string will be parsed into a Python list and used to update the specified column in the database.

## Example CSV:

| id  | topics_list                    |
| --- | ------------------------------ |
| 1   | ["topic1", "topic2"]           |
| 2   | ["topic3", "topic4"]           |
| 3   | ["topic5", "topic6", "topic7"] |

| id  | categories_list                         |
| --- | --------------------------------------- |
| 1   | ["category1", "category2"]              |
| 2   | ["category3", "category4"]              |
| 3   | ["category5", "category6", "category7"] |

## Logging

The script will log progress, warnings, and errors to the console. Key events include:

    • Successful updates to the database.
    • Skipping rows with invalid topics_list/categories_list.
    • Errors during the execution of database operations.

## Error Handling

    • Invalid topics_list/categories_list: Rows with an invalid or incorrectly formatted topics_list/categories_list are skipped with a warning logged.
    • Database Errors: Any errors during communication with Supabase (e.g., API errors, failed updates) will be logged as errors.

## License

This project is licensed under the MIT License.
