import polars as pl
import asyncio
import random
from search import es, products_mapping, products_index_name

async def load_dataset():
    # Load the CSV dataset with Polars
    df = pl.read_csv("fashion.csv")

    # Remove the "Image" column
    df = df.drop("Image")

    # Convert the DataFrame to a list of dictionaries for each document
    records = df.to_dicts()

    # Insert each document into ElasticSearch
    for record in records:
        # Generate a random price between 1 and 100,000
        price = random.uniform(1, 100000)

        # Adjust the field names as per the ElasticSearch mapping
        document = {
            "ProductId": record["ProductId"],
            "Gender": record["Gender"],
            "SubCategory": record["SubCategory"],
            "ProductType": record["ProductType"],
            "Colour": record["Colour"],
            "Usage": record["Usage"],
            "ProductTitle": record["ProductTitle"],
            "ImageUrl": record["ImageURL"],
            "Price": price
        }

        # Insert into ElasticSearch
        await es.insert_document(products_index_name, document)

    print(f"Inserted {len(records)} documents into ElasticSearch.")

# Run the async task
asyncio.run(load_dataset())
