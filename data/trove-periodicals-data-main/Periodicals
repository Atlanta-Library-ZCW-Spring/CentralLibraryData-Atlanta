import pandas as pd

#loading both periodical datasets into a dataframe
titles_df = pd.read_csv("periodical-titles.csv")
issues_df = pd.read_csv("periodical-issues.csv")

#cleaning data and columns/exploration
#print(titles_df.columns)
#print(issues_df.columns)

#print(titles_df.head())
#print(issues_df.head())

#merged df on unique id key
def merge_data(titles_df, issues_df):
    merged_df = pd.merge(titles_df, issues_df, left_on="id", right_on="title_id")
    return merged_df

merged_df = merge_data(titles_df, issues_df)



#details on merged df for exploration
#print(merged_df.shape)
#print(merged_df.columns[:6])
#print(merged_df.head(20))


#print(merged_df.columns.tolist()) #returns merged df columns index into a python list of strings;doesnt modify it just returns/displays them
#print(merged_df[["description_x"]].head(30)) #returns 30 lines of titles.description 
#print(merged_df[["description_y"]].head(30)) #returns 30 lines of issues.description

# Fill missing descriptions
merged_df["description_y"] = merged_df["description_y"].fillna("")

# Extract volume number
merged_df["volume"] = merged_df["description_y"].str.extract(
    r"(?:Volume|Vol\.)\s*(\d+)",
    expand=False
)

# Extract issue number
merged_df["issue"] = merged_df["description_y"].str.extract(
    r"(?i)(?:Issue|No\.?|Number)\s*(\d+)",
    expand=False
)

# Rename place to location
merged_df["location"] = merged_df["place"]

# Quick checks
print("Missing descriptions:",
      merged_df["description_y"].isna().sum())

print("Contains 'Volume':",
      merged_df["description_y"].str.contains("Volume", na=False).sum())

print("Contains 'Vol.':",
      merged_df["description_y"].str.contains("Vol.", regex=False, na=False).sum())

clean_df = merged_df[ #created a new merged df with only the fields i need to send to java
    [
        "title_x",
        "publisher",
        "issn",
        "location",
        "date",
        "pages",
        "description_y",
        "volume",
        "issue"
    ]
].copy() 

clean_df.rename(
    columns={
        "title_x": "title",
        "date": "publicationDate",
        "description_y": "description"
    },
    inplace=True
)

print(clean_df.columns)
print(clean_df.head())
print(clean_df.info()) #shows column names, missing values, and data types

print(clean_df[["description", "volume", "issue"]].head(20))

#JSON export

clean_df.to_json(
    "clean_periodicals.json",
    orient="records",
    indent=4
)

print("JSON files created successfully!")

# Export first 30 records only
clean_df.head(30).to_json(
    "clean_periodicals_30.json",
    orient="records",
    indent=4
)

print("30-record JSON file created successfully!")

#print(titles_df[["id", "title"]].head())
#print(issues_df[["title_id", "title"]].head())

#merge_df = pd.merge(issues_df, titles_df, on="title", how="inner")
#print(merge_df.head())

