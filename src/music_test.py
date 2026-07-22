# Test
import pandas as pd

music_df = pd.read_json("music_data.json")

print(f"Number of records: {len(music_df)}")
print("First record:", music_df.iloc[0].to_dict())