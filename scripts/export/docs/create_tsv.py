import sys
import yaml
import pandas as pd


def main():
    if len(sys.argv) != 2:
        raise RuntimeError(
            f"Please provide input file path as sole argument to create_tsv.py"
        )
    input_file = sys.argv[1]

    with open(input_file) as f:
        data = yaml.load(f, Loader=yaml.SafeLoader)

    df_data = {
        "key": [],
        "type": [],
        "description": [],
        "display_name": [],
        "function 1": [],
        "sub key 1": [],
        "params 1": [],
        "function 2": [],
        "sub key 2": [],
        "params 2": [],
        "function 3": [],
        "sub key 3": [],
        "params 3": [],
        "function 4": [],
        "sub key 4": [],
        "params 4": [],
    }

    for val_str in ["validators", "prefix_validators"]:
        if data.get(val_str):
            ite = 0
            for key, content in data[val_str].items():
                df_data["key"].append(key)
                df_data["type"].append(val_str)
                key_metadata = content.get("key_metadata", {})
                df_data["description"].append(key_metadata.get("description", ""))
                df_data["display_name"].append(key_metadata.get("display_name", ""))
                static_mappings = content.get("static_mappings", {})
                validators = content.get("validators", {})
                for i in range(len(validators)):
                    df_data["function " + str(i + 1)].append(
                        validators[i]["callable_builder"]
                    )
                    if validators[i].get("parameters"):
                        params = ""
                        for sub_key, sub_val in validators[i]["parameters"].items():
                            if "key" in sub_key:
                                df_data["sub key " + str(i + 1)].append(sub_val)
                            else:
                                params += str(sub_key) + " " + str(sub_val) + ";"
                        df_data["params " + str(i + 1)].append(params)

                    if len(df_data["sub key " + str(i + 1)]) < len(df_data["key"]):
                        df_data["sub key " + str(i + 1)].append("")
                    if len(df_data["params " + str(i + 1)]) < len(df_data["key"]):
                        df_data["params " + str(i + 1)].append("")
                for i in range(len(validators), 4):
                    df_data["function " + str(i + 1)].append("")
                    df_data["sub key " + str(i + 1)].append("")
                    df_data["params " + str(i + 1)].append("")
                # print(f"iteration {ite}: ", {k:len(v) for k,v in df_data.items()})
                ite += 1
    df = pd.DataFrame.from_dict(df_data)

    output_file = input_file.split(".")[0] + ".tsv"
    df.to_csv(output_file, sep="\t", index=False)
    print(f"    tsv viewer file for {input_file} written to {output_file}.")


if __name__ == "__main__":
    main()
