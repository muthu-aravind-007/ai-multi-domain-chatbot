import xml.etree.ElementTree as ET
import json
import os

data_folder = "MedQuAD-master"
output_file = "data/medical.json"

qa_list = []
limit = 100  # enough

for root_folder, dirs, files in os.walk(data_folder):
    for file in files:
        if file.endswith(".xml"):
            path = os.path.join(root_folder, file)

            try:
                tree = ET.parse(path)
                root = tree.getroot()

                for qa in root.findall(".//QAPair"):
                    question = qa.findtext("Question")
                    answer = qa.findtext("Answer")

                    if question and answer:
                        qa_list.append({
                            "question": question.strip(),
                            "answer": answer.strip()
                        })

                    if len(qa_list) >= limit:
                        break

            except:
                continue

        if len(qa_list) >= limit:
            break

    if len(qa_list) >= limit:
        break

# Save
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(qa_list, f, indent=2)

print(f"✅ Extracted {len(qa_list)} medical QA pairs")