from IPython.display import display, HTML
import pandas as pd
import matplotlib.pyplot as plt
import math
from io import BytesIO
import base64

plt.style.use("ggplot")

def display_in_grid(notes_list=None, html_list=None):
    """
    Creates and displays a grid containing the content passed via the parameters

    Parameters:
    notes_list (list): A list of strings representing notes which will be displayed in a dedicated cell of the grid.
    html_list (list): A list of strings each respresenting some HTML which should be rendered in a seperate grid cell.
    """

    html = "<div style='display: flex; flex-wrap: wrap;'>"
    if notes_list:
        list_html = "<ul style='list-style-type: none; padding: 0; margin: 0; text-align: left;'>" + \
                    "".join(f"<li style='margin: 5px 0;'>- {item}</li>" for item in notes_list) + \
                    "</ul>"
        html += f"""
            <div style='margin: 10px; padding: 10px; border: 1px solid #ccc; text-align: left;'>
                <h4>Notes</h4>
                {list_html}
            </div>
        """
    if html_list:   
        for html_block in html_list:
            html += f"""
                <div style='margin: 10px; padding: 10px; border: 1px solid #ccc;'>
                    {html_block}
                </div>
            """
    html += "</div>"
    display(HTML(html))

def create_bicategorical_pie_chart(total_count, second_category_count, first_category_label, second_category_label):
    """
    Creates a pie chart displaying the distribution of a binary attribute together with the percentages occupied
    by both categories.

    Parameters:
    total_count (int): The total number of observations.
    second_category_count (int): The number of observations belonging to the second category.
    first_category_label (string): A short description for the first category displayed in the chart.
    second_category_label (string): A short description fot the second category displayed in the chart.

    Returns:
    string: HTML embedding a picture of the created chart.
    """
    
    valid_count = total_count - second_category_count
    labels = [first_category_label, second_category_label]
    values = [valid_count, second_category_count]

    # create pie chart
    fig, ax = plt.subplots(figsize=(3.5, 3.5))
    wedges, texts, autotexts = ax.pie(
        values,
        autopct=lambda p: '{:.1f}%'.format(p, p * total_count / 100) if p != 0.0 else "",
        startangle=180,
        textprops={'fontsize': 12}
    )
    ax.axis('equal')

    # add legend
    ax.legend(
        wedges,
        labels,
        loc="lower right",
        fontsize=7,         # Smaller font size for labels
        title_fontsize=8,   # Smaller title font size
        bbox_to_anchor=(0.7, 1.0)  # Position the legend slightly outside the chart
    )

    # save chart to BytesIO object
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png', bbox_inches='tight')
    plt.close(fig) 

    # encode image in base64 for embedding in HTML
    img_buffer.seek(0)
    base64_img = base64.b64encode(img_buffer.read()).decode('utf-8')
    return f"<img src='data:image/png;base64,{base64_img}' style='display: block; margin: 0 auto;'>"


def explore_numerical_id(column):
    """
    Explores a column of a pandas dataframe containing numerical primary or foreign keys:
    1) missing/faulty values
    - displays whether column contains only valid numbers (of type int/float excluding nan, inf, -inf)
    - if present displays non-numbers and how often they occur
    2) integer values
    - displays whether contained number entries are all integer and therefore save to cast to int (includes integer floats)
    2) duplicates 
    - displays whether number entries contain no duplicates
    - if present displays values for which there are duplicates

    Parameters:
    column (pandas.Series): A single column of a pandas dataframe. (e.g. obtained by df['column_name'])
    """

    column = column.reset_index(drop=True)
    messages = []
    html_list = []
    if len(column) == 0:
        messages.append("column is empty")
    else:
        def is_non_number(value):
            if isinstance(value, (int, float)):
                return math.isnan(value) or math.isinf(value)
            return True
        
        non_number_mask = column.apply(is_non_number)
        contains_non_numbers = any(non_number_mask)
        if not contains_non_numbers:
            messages.append("contains only valid numbers")

        if contains_non_numbers:
            non_numbers = column[non_number_mask]
            non_numbers_with_types = non_numbers.apply(lambda x: f"{x} ({type(x).__name__})")
            non_numbers_counts = non_numbers_with_types.value_counts(dropna=False)
            non_numbers_counts_df = pd.DataFrame(non_numbers_counts).reset_index()
            non_numbers_counts_df.columns = ['contained non-numbers', 'count']
            non_number_counts_html = non_numbers_counts_df.to_html(index=False)
            html_list.append(non_number_counts_html)

        numbers = column[~non_number_mask]
        numbers_are_all_integer = numbers.apply(lambda x: isinstance(x, int) or (isinstance(x, float) and x.is_integer())).all()
        if numbers_are_all_integer:
            messages.append("number entries can be savely casted to int")

        numbers_contain_duplicates = len(numbers.unique()) != len(numbers)
        if numbers_contain_duplicates:
            duplicated_values = numbers[numbers.duplicated(keep=False)].unique()
            duplicated_values_df = pd.DataFrame({'contained duplicates': duplicated_values})
            duplicated_values_df_html = duplicated_values_df.head(15).to_html(index=False)
            if len(duplicated_values_df) > 15:
                truncated_html = "<p style='color: grey;'>(truncated to 15 rows)</p>"
                combined_html = f"{duplicated_values_df_html}{truncated_html}"
            else:
                combined_html = duplicated_values_df_html
            
            html_list.append(combined_html)

        if not numbers_contain_duplicates:
            messages.append("numerical entries contain no duplicates")

    display_in_grid(messages, html_list)


def explore_string_id(column):
    """
    Explores a column of a pandas dataframe containing string primary or foreign keys:
    1) missing/faulty values
    - displays whether column contains only entries of type string
    - if present displays non-string values and how often they occur
    2) occuring lengths 
    - displays occuring string lengths
    3) duplicates 
    - displays whether valid entries contain duplicates
    - if present displays duplicates contained in the valid entries and how often they occur

    Parameters:
    column (pandas.Series): A single column of a pandas dataframe. (e.g. obtained by df['column_name'])
    """

    column = column.reset_index(drop=True)
    messages = []
    html_list = []
    
    if len(column) == 0:
        messages.append("column is empty")
    else:
        contains_non_strings = any(column.apply(lambda x: not isinstance(x, str)))
        if contains_non_strings:
            non_string_entries = column[column.apply(lambda x: not isinstance(x, str))]
            non_string_counts = non_string_entries.value_counts(dropna = False)
            non_string_df = pd.DataFrame(non_string_counts).reset_index()
            non_string_df.columns = ['contained non-strings', 'count']
            non_string_html = non_string_df.to_html(index=False)
            html_list.append(non_string_html)
            
        if not contains_non_strings:
            messages.append("contains only valid strings")
        
        string_entries = column[column.apply(lambda x: isinstance(x, str))]
        id_lengths = string_entries.apply(lambda x: len(str(x))).unique()
        id_lengths_df = pd.DataFrame({'occurring string lengths': id_lengths})
        id_lengths_html = id_lengths_df.to_html(index=False)
        html_list.append(id_lengths_html)
        
        
        strings_contain_duplicates = len(string_entries.unique()) != len(string_entries)
        if strings_contain_duplicates:
            duplicated_values = string_entries[string_entries.duplicated(keep=False)].unique()
            duplicated_values_df = pd.DataFrame({'entries with duplicates': duplicated_values})
            duplicated_values_df_html = duplicated_values_df.head(15).to_html(index=False)
            if len(duplicated_values_df) > 15:
                truncated_html = "<p style='color: grey;'>(truncated to 15 rows)</p>"
                combined_html = f"{duplicated_values_df_html}{truncated_html}"
            else:
                combined_html = duplicated_values_df_html
            html_list.append(combined_html)
            
        if not strings_contain_duplicates:
            messages.append("valid entries contain no duplicates")
        
    display_in_grid(messages, html_list)


def explore_boolean_attribute(column):
    """
    Explores a column of a pandas dataframe containing entries representing boolean values:
    1) missing/faulty values
    - displays whether column contains only typical boolean encodings.
    - if present displays non-boolean entries and how often they occur
    3) distribution
    - displays contained boolean representations ans how often they occur
    - renders a pie chart displaying both the percentages of entries encoding True and False

    Parameters:
    column (pandas.Series): A single column of a pandas dataframe. (e.g. obtained by df['column_name'])
    """

    column = column.reset_index(drop=True)
    messages = []
    html_list = []
    
    if len(column) == 0:
        messages.append("column is empty")
    else:
        positive_bools = [True, 1, 1.0, "Yes", "yes", "Positive", "positive", "Y", "y", "T", "t"]
        negative_bools = [False, 0, 0.0, "No", "no", "Negative", "negative", "N", "n", "F", "f", None]
        bool_values = positive_bools + negative_bools
        
        def is_negative(value):
            return value in negative_bools
        
        def is_bool(value):
            return value in bool_values

        contains_non_bools = any(column.apply(lambda x: not is_bool(x)))
        if contains_non_bools:
            non_bool_entries = column[column.apply(lambda x: not is_bool(x))]
            non_bool_entries_with_types = non_bool_entries.apply(lambda x: f"{x} ({type(x).__name__})")
            non_bool_counts = non_bool_entries_with_types.value_counts(dropna=False)
            non_bool_df = pd.DataFrame(non_bool_counts).reset_index()
            non_bool_df.columns = ['faulty/unknown entries', 'count']
            non_bool_html = non_bool_df.to_html(index=False)
            html_list.append(non_bool_html)

        if not contains_non_bools:
            messages.append("contains only boolean representations")
        
        contained_representations = column[column.apply(lambda x: is_bool(x))]
        contained_representation_with_types = contained_representations.map(lambda x: f"{x} ({type(x).__name__})") 
        representations_counts = contained_representation_with_types.value_counts(dropna=False)
        representations_counts_df = pd.DataFrame(representations_counts).reset_index()
        representations_counts_df.columns = ['contained booleans representations', 'count']
        representations_counts_html = representations_counts_df.to_html(index=False)
        html_list.append(representations_counts_html)
        
        contained_bools = contained_representations.apply(lambda x: False if is_negative(x) else True)
        contained_positives = contained_bools[contained_bools]
        chart_html = create_bicategorical_pie_chart(len(contained_bools), len(contained_positives), "values repres. False", "values repres. True")
        html_list.append(chart_html)
    
    display_in_grid(messages, html_list)


def explore_categorical_attribute(column):
    """
    Explores a column of a pandas dataframe containing categorical entries:
    1) distribution
    - renders a bar chart displaying the number of occurences for all contained categories

    Parameters:
    column (pandas.Series): A single column of a pandas dataframe. (e.g. obtained by df['column_name'])
    """

    column = column.reset_index(drop=True)
    messages = []
    html_list = []

    if len(column) == 0:
        messages.append("column is empty")
    else:
        counts = column.value_counts(dropna=False)
        fig, ax = plt.subplots(figsize=(8, 6))
        counts.plot(kind="bar", ax=ax, legend=False)
        
        for i, v in enumerate(counts):
            ax.text(i, v + 0.1, str(v), ha='center', va='bottom', fontsize=10)
        
        ax.set_xticks(range(len(counts)))
        ax.set_ylabel("Count")
        plt.tight_layout()
        
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png', bbox_inches='tight')
        plt.close(fig)

        img_buffer.seek(0)
        base64_img = base64.b64encode(img_buffer.read()).decode('utf-8')
        chart_html = f"<img src='data:image/png;base64,{base64_img}' style='display: block; margin: 0 auto;'>"
        html_list.append(chart_html)
    
    display_in_grid(messages, html_list)


def explore_numerical_attribute(column):
    """
    Explores a column of a pandas dataframe containing numerical entries:
    1) missing/faulty values
    - displays whether column contains only valid numbers (of type int/float excluding nan, inf, -inf)
    - if present displays non-numbers and how often they occur
    2) number type
    - displays whether valid number entries contain only ints, only floats, or both ints and floats
    3) distribution
    - displays mean, median, standard deviation and range of the valid entries
    - renders two boxplots with and without outliers

    Parameters:
    column (pandas.Series): A single column of a pandas dataframe. (e.g. obtained by df['column_name'])
    """
    column = column.reset_index(drop=True)
    messages = []
    html_list = []
    
    if len(column) == 0:
        messages.append("column is empty")
    else:
        def is_non_number(value):
            if isinstance(value, (int, float)):
                return math.isnan(value) or math.isinf(value)
            return True
        
        non_number_mask = column.apply(is_non_number)
        contains_non_numbers = any(non_number_mask)
        if not contains_non_numbers:
            messages.append("contains only valid numbers")
        
        numbers = column[~non_number_mask]
        contains_only_ints = all(column.apply(lambda x: isinstance(x,int)))
        valid_numbers_contain_only_ints = all(numbers.apply(lambda x: isinstance(x,float) and x.is_integer())) and len(numbers) > 0
        valid_numbers_contain_only_floats= all(numbers.apply(lambda x: isinstance(x,float) and not x.is_integer())) and len(numbers) > 0
        if contains_only_ints:
            messages.append("column contains only ints")
        elif valid_numbers_contain_only_ints:
            messages.append("valid number entries contain only ints")
        elif valid_numbers_contain_only_floats:
            messages.append("valid number entries contain only floats")
        elif len(numbers) > 0:
            messages.append("valid number entries contain ints and floats")
        
        
        min_value = round(numbers.min(),3)
        max_value = round(numbers.max(),3)
        mean = round(numbers.mean(),3)
        median = round(numbers.median(),3)
        sd = round(numbers.std(),3)
        messages.append(f"mean: {mean}")
        messages.append(f"median: {median}")
        messages.append(f"standard deviation: {sd}")
        messages.append(f"range: [{min_value},{max_value}]")
        
        column_name = column.name
        variable_name = column_name if column_name is not None else 'variable'

        # Create the first boxplot (with outliers)
        fig1, ax1 = plt.subplots(figsize=(2.75, 3.5))
        ax1.boxplot(numbers, showfliers=True)
        ax1.set_title("with outliers")
        ax1.set_xlabel(variable_name)
        ax1.set_ylabel('Values')
        plt.tight_layout()
        img_buffer1 = BytesIO()
        plt.savefig(img_buffer1, format='png', bbox_inches='tight')
        plt.close(fig1)
        img_buffer1.seek(0)
        base64_img1 = base64.b64encode(img_buffer1.read()).decode('utf-8')
        boxplot_html_with_outliers = f"<img src='data:image/png;base64,{base64_img1}' style='display: block; margin: 0 auto;'>"
        html_list.append(boxplot_html_with_outliers)
        
        # Create the second boxplot (without outliers)
        fig2, ax2 = plt.subplots(figsize=(2.75, 3.5))
        ax2.boxplot(numbers, showfliers=False)
        ax2.set_title("without outliers")
        ax2.set_xlabel(variable_name)
        ax2.set_ylabel('Values')
        plt.tight_layout()
        img_buffer2 = BytesIO()
        plt.savefig(img_buffer2, format='png', bbox_inches='tight')
        plt.close(fig2)
        img_buffer2.seek(0)
        base64_img2 = base64.b64encode(img_buffer2.read()).decode('utf-8')
        boxplot_html_without_outliers = f"<img src='data:image/png;base64,{base64_img2}' style='display: block; margin: 0 auto;'>"
        html_list.append(boxplot_html_without_outliers)
        
        if contains_non_numbers:
            non_numbers = column[non_number_mask]
            create_bicategorical_pie_chart(len(column),len(non_numbers), "valid entries", "non-valid entries")
            non_numbers_with_types = non_numbers.apply(lambda x: f"{x} ({type(x).__name__})")
            non_numbers_counts = non_numbers_with_types.value_counts(dropna=False)
            non_numbers_counts_df = pd.DataFrame(non_numbers_counts).reset_index()
            non_numbers_counts_df.columns = ['contained non-numbers', 'count']
            non_number_counts_html = non_numbers_counts_df.to_html(index=False)
            html_list.append(non_number_counts_html)
    
    display_in_grid(messages, html_list)