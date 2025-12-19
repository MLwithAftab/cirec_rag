python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
http://localhost:8000/admin enter the password() and username() to upload the documents once uploaded use this http://localhost:8000/


---

## 📊 Expected Output

Now you should see:
```
Processing .xlsx file: CE Prices.xlsx
  Found product: Central European Ethylene
  ...
Excel: Created 2437 searchable entries
✓ Successfully added 2437 chunks to index

Processing .docx file: CMN414.docx
  Word doc has 45 paragraphs, split into 23 chunks  ← BETTER!
Word: Extracted 23 chunks
✓ Successfully added 23 chunks to index

Processing .pdf file: CMN414.pdf
  PDF has 18 pages
  Split into 34 chunks  ← MUCH BETTER!
PDF: Extracted 34 chunks
✓ Successfully added 34 chunks to index
```

---

## 🎯 Test All Document Types

After re-uploading, test these:

### **Test 1: Excel (Already Working)** ✅
```
What was the average Central European ethylene price in May 2024?
```

### **Test 2: PDF Content** 🔍
```
Compare Russian ethylene production in Q1 2024 versus Q1 2025
```

### **Test 3: Word Content** 📄
```
How did MOL's petrochemical margins perform?
```

### **Test 4: Multi-Source** 🌟
```
What were Czech crude imports in Jan-Mar 2025?





# **Expected answer and outputs**:
What do you know about MOL petrochemical production Jan-Mar 2025?
Based on the given information, the known production values for MOL petrochemical production Jan-Mar 2025 are: - Ethylene: 171,000 tons - Propylene: 89,000 tons - Butadiene: 15,000 tons - Raffinate: 26,000 tons  Since there is no new context provided, the answer remains the same.  Final Answer: The known production values for MOL petrochemical production Jan-Mar 2025 are:  - Ethylene: 171,000 tons - Propylene: 89,000 tons - Butadiene: 15,000 tons - Raffinate: 26,000 tons.

How did MOL's petrochemical margins perform?
Answer
To determine how MOL's petrochemical margins performed, we need to look at the information provided in the context.  According to the context, MOL's petrochemical margins dropped to €151 per ton in the first quarter of 2025, compared to €209 per ton in the first quarter of the previous year and €167 in the fourth quarter of the previous year.  However, in the second quarter of 2025, MOL's petrochemical margins increased to €234 per ton, which is the highest figure since the second quarter of 2022.  Despite the increase in the second quarter, the context states that MOL's petrochemicals remain loss-making due to the continuing stagnation and slowdown in European demand.  Since there is no new context provided, the initial analysis remains the same.   Therefore, MOL's petrochemical margins initially dropped but then increased in the second quarter of 2025.  Final Answer: MOL's petrochemical margins initially dropped to €151 per ton in Q1 2025 but then increased to €234 per ton in Q2 2025.

What were Czech crude imports in Jan-Mar 2025?
Answer
To find the Czech crude imports in Jan-Mar 2025, we need to look at the given data.   According to the text, the total Czech crude imports in Jan-Mar 2025 were 1.433 million tons, which is the sum of the imports from the following countries: - Azerbaijan: 656,200 tons - Kazakhstan: 255,500 tons - Russia: 521,300 tons  The correct calculation is: 1,433,000 = 656,200 + 255,500 + 521,300  So, the total Czech crude imports in Jan-Mar 2025 were 1,433,000 tons (or 1.433 million tons).  Since there's no new context provided that adds useful data, the answer remains the same.  Final Answer: The Czech crude imports in Jan-Mar 2025 were 1,433,000 tons (or 1.433 million tons).

Show me the trend of Central European ethylene prices from 2023 to 2025:
Answer
To show the trend of Central European ethylene prices from 2023 to 2025, we need to look at the average prices for each year.   From the data, we have the following average prices for each month:  2023: - March: €1245.37 per ton - April: €1158.53 per ton - June: €1161.39 per ton - September: €1105.52 per ton - December: €1236.46 per ton  2025: - March: €1323.03 per ton - April: €1219.20 per ton  Since we don't have data for all months in 2025 and the data for 2023 is not complete for all months either, we can't accurately calculate the average price for each year. However, we can observe the trend from the available data.  In 2023, the prices seem to fluctuate: - March: €1245.37 per ton (high) - April: €1158.53 per ton (lower) - June: €1161.39 per ton (slightly higher than April) - September: €1105.52 per ton (lower) - December: €1236.46 per ton (higher)  From 2023 to 2025, the available data shows: - March 2023: €1245.37 per ton - March 2025: €1323.03 per ton (higher) - April 2023: €1158.53 per ton - April 2025: €1219.20 per ton (higher)  Based on the available data, the trend seems to be an increase in prices from 2023 to 2025, but the data is limited and not comprehensive for all months. Therefore, the statement is:  The Central European ethylene prices seem to be increasing from 2023 to 2025 based on the available data.