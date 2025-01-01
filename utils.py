
from openai import OpenAI

client = OpenAI(
    base_url='https://expert-eft-innocent.ngrok-free.app/v1', api_key='na')


def get_chat_completion(prompt):
    response = client.chat.completions.create(
        model="gemma-2-9b-instruct",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0,
    )
    return response.choices[0].message.content


def get_llm_response(pdf_data, json_template):
    prompt = f"""
                You are an AI assistant specializing in extracting structured data from medical billing documents. 
                Your task is to parse the provided billing PDF data and populate a JSON structure for each billing entry with precise key-value pairs, ensuring each amount, code, and description is assigned to its correct field and that each record contains all specified keys, even if they are blank (""). 
                Follow these instructions to prevent misallocation of values, especially with respect to amounts:

                1. Analyze all billing elements: Analyze ALL TEXT ELEMENTS, TABLE CELLS AND FORM FIELDS in the PDF document.

                2. Field-specific Allocation:

                    FEATURE_TYPE: The feature type will generally be one of the following:
                    ['Lab', 'Stage', 'Treatment', 'Symptoms', 'Factor', 'Medical',
                    'Impairment']
                    FEATURE: VERY CAREFULLY Look for which the MEDICAL TEST was done. This can be generally like Sodium, potassium etc
                    DATE: The DATE when the MEDICAL TEST was performed
                    VALUE: Extract The EXACT VALUE OF THE TEST which was undertaken.
                    UNIT_OF_MEASUREMENT: This is the UNIT in which the TEST IS MEASURED. e.g. mmol/L, mg/dL, mL/min/1.73m2 etc.
                    REFERENCE_RANGE: The REFERENCE RANGE for the MEDICAL TEST.
                    CONDITION_STATUS: Based on the REFERENCE RANGE and ACTUAL VALUE, this value will be filled. can take values like low, high, normal, abnormal. The classification will be done based on the ACTUAL TEST VALUE AND THE REFERNCE RANGE. 
                        IF THE ACTUAL VALUES IS LOWER THAN MINIMUM REFERENCE RANGE THIS VALUE WILL BE LOW. IF ITS WITHIN THE RANGE IT WILL BE NORMAL, IF ITS ABOVE THE MAXIMUM RANGE IT WILL BE ABOVE.

                3. Formatting:

                    Output each record as FIELD_NAME=VALUE pairs.
                    Begin each record with FEATURE_TYPE=TYPE OF FEATURE. one of ['Lab', 'Stage', 'Treatment', 'Symptoms', 'Factor', 'Medical',
                    'Impairment']
                
                5. Positive Values Only: Convert any extracted negative values to positive for numerical fields.

                6. Consistency and Verification: Each record should include every key with appropriate values or blank entries. Double-check allocations to confirm that each value strictly adheres to its designated key and no field is filled incorrectly.

                7. No Hallucination: Do not generate or infer any information not present in the data.

                8. MAKE SURE VERY STRICTLY THAT YOU DO NOT include any explanatory text, prefixes, or suffixes. Only provide the key-value pairs.

                Template JSON structure for each billing item:
                {json_template}

                VALIDATION:
                - Double-check each record to verify that every key is present with the correct values or is blank as needed. This ensures no missing keys across all entries.
                - After extraction, Make sure that EACH AND EVERY RECORD IS CONSISTANT in terms of the KEYS they have.
                - MAKE SURE THAT ALL THE FOLLOWING KEYS ARE PRESENT FOR EACH RECORD
                        a. "FEATURE_TYPE"
                        b. "FEATURE"
                        c. "DATE"
                        d. "VALUE"
                        e. "UNIT_OF_MEASUREMENT"
                        f. "REFERENCE_RANGE"
                        g. "CONDITION_STATUS"

                Analyze the parsed data from the billing PDF, following the template JSON format. Extract each billing item and output the structured key-value pairs, beginning each item with FEATURE_TYPE
                {pdf_data}
                """
    response = get_chat_completion(prompt)
    return response
