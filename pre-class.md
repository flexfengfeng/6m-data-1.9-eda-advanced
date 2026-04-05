# **Pre-Class Study Guide: Advanced EDA**

⏱️ **Estimated Duration:** 30 Minutes
**Prerequisites:** Lesson 1.8 — EDA Basic

> In Lesson 1.8 you cleaned messy datasets using descriptive statistics, handled missing values, and transformed string data. This lesson goes further: you'll learn to analyse relationships between columns (correlation), reshape data between wide and long formats, work with time-series dates, and summarise groups using Split-Apply-Combine logic.

**Goal:** Build your mental model for these operations *before* working through the code. Understanding the *why* makes the syntax much easier to absorb.

**Video Intro:** [Advanced EDA](https://youtu.be/IzujGGRYjkQ)

## **1\. Key Concepts to Master**

Please review the following four concepts. You don't need to memorize code syntax yet—just understand the logic.

### **A. Correlation vs. Covariance**

* **The Problem:** We want to know if two stocks (e.g., MSFT and IBM) move together.  
* **Covariance:** Tells us *if* they move in the same direction, but the number is hard to interpret (e.g., is "0.0004" a strong relationship? It depends on the scale of the data).  
* **Correlation:** A normalized version of covariance. It is always between **\-1 and 1**.  
  * 1: Perfect match (they move identically).  
  * \-1: Perfect inverse (one goes up, one goes down).  
  * 0: No relationship (random).  
* **Reading:** [What’s the Difference Between Covariance and Correlation](https://careerfoundry.com/en/blog/data-analytics/covariance-vs-correlation/)

### **B. Time is an Object, Not a String**

* **The Problem:** To a computer, the text "2023-01-01" is just a string of characters, like "Hello World". It doesn't know that "2023-01-02" comes one day after it.  
* **The Solution:** We convert these strings into **Datetime Objects**. This allows us to do math on dates (e.g., Date\_B \- Date\_A \= 3 days) and handle business days vs. weekends.  
* **Reading:** [Python Datetime Tutorial](https://www.programiz.com/python-programming/datetime)

### **C. Tidy Data (Wide vs. Long)**

* **Wide Format (Excel Style):** Great for humans.  
  * *Example:* A column for "2020 Sales", a column for "2021 Sales", etc.  
  * *Problem:* Hard to plot or group by "Year" because "Year" isn't a column; it's a header.  
* **Long Format (Database Style):** Great for code/pandas.  
  * *Example:* One column called "Year" (containing 2020, 2021\) and one column called "Sales".  
  * *Action:* We use **Melt** to go from Wide $\\to$ Long, and **Pivot** to go from Long $\\to$ Wide.

### **D. Split-Apply-Combine**

This is the logic behind the famous groupby operation.

1. **Split** the data into groups (e.g., Split restaurant tips by "Smoker" vs. "Non-Smoker").  
2. **Apply** a function to each group independently (e.g., Calculate the average tip).  
3. **Combine** the results back into a summary table.

## **2\. AI Companion Exercise (Highly Recommended)**

Use an AI assistant (ChatGPT or Claude) to solidify these concepts by working through the prompts below. This is a great substitute for a study group if you're learning solo.

Copy and paste the prompts below into your AI assistant.

**Prompt 1 (Data Merging):**

"I am learning pandas dataframes. Explain the difference between an 'Inner Join' and a 'Left Join' using a simple analogy, like inviting friends to two different parties. What happens to the friends who are only on one list?"

**Prompt 2 (Reshaping):**

"Explain the difference between pandas pivot and melt. Give me an example using a spreadsheet of student grades to show why I might want to switch between them."

**Prompt 3 (Grouping):**

"Explain the 'Split-Apply-Combine' strategy in data analysis using a simple real-world example, like calculating the average price of different fruit types in a grocery cart."

## **3\. Useful Reference Sheets**

Keep these open during the class. They are excellent for looking up syntax quickly.

* [Pandas Data Wrangling Cheatsheet](https://www.datacamp.com/cheat-sheet/pandas-cheat-sheet-data-wrangling-in-python)  
* [Working with Dates and Times in Python](https://www.datacamp.com/cheat-sheet/working-with-dates-and-times-in-python-cheat-sheet)

## **4\. Check for Understanding**

Before moving on, can you answer "Yes" to the following?

* \[ \] I understand that NaN stands for "Not a Number" (missing data) and usually needs to be filled or dropped.
* \[ \] I know that if I merge two tables using an **Inner Join**, rows that don't match in both tables will be deleted.
* \[ \] I understand that to analyze stock trends over time, my data must be sorted chronologically by an Index.
* \[ \] I know that pivot\_table in Python is the equivalent of Pivot Tables in Excel.

<details>
<summary>💡 Suggested Answers</summary>

**NaN (Not a Number):** True — NaN is Pandas' placeholder for missing data. You must handle it before aggregating, plotting, or feeding data to a model, because most operations propagate or error on NaN.

**Inner Join deletes non-matching rows:** True — an Inner Join only keeps rows where the key exists in *both* tables. If a customer has no orders, they disappear. Use a Left Join to keep all customers regardless.

**Time-series must be sorted chronologically:** True — operations like `.resample()`, `.rolling()`, and forward-fill (`.ffill()`) assume the index goes from earliest to latest. Unsorted dates produce nonsensical results. Use `df.sort_index()` after setting a DatetimeIndex.

**pivot_table ≈ Excel Pivot Tables:** True — `df.pivot_table(index=..., columns=..., values=..., aggfunc=...)` replicates the drag-and-drop logic of Excel's pivot tables. The `aggfunc` argument (e.g., `'mean'`, `'sum'`) corresponds to choosing the "Value Field Settings" in Excel.

</details>

If you are unsure about any of these, re-read the relevant section above or post your question in the **#questions** channel on Discord.


