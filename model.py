import csv

# Define the input and output file paths
input_file = 'input.csv'
output_file = 'output.csv'

# Function to swap columns A and B in the CSV file
def swap_columns(input_file, output_file):
    # Open the input CSV file in read mode
    with open(input_file, 'r') as csvfile:
        # Create a CSV reader object
        reader = csv.reader(csvfile)
        
        # Check if there are at least two columns
        header = next(reader)
        if len(header) < 2:
            raise ValueError("The CSV file must have at least two columns.") 

        # Swap columns A and B in the header
        header[0], header[1] = header[1], header[0]

        # Open the output CSV file in write mode
        with open(output_file, 'w', newline='') as outfile:
            # Create a CSV writer object
            writer = csv.writer(outfile)
            # Write the modified header to the output file
            writer.writerow(header)
            # Iterate over each row in the input file
            for row in reader:
                # Check if the row has at least two columns
                if len(row) < 2:
                    raise ValueError("Each row in the CSV file must have at least two columns.")
                
                # Swap columns A and B in each row
                row[0], row[1] = row[1], row[0]
                # Write the modified row to the output file
                writer.writerow(row)

# Call the swap_columns function
try:
    swap_columns(input_file, output_file)
    print("CSV file processed successfully.")
except Exception as e:
    print("Error:", str(e))
