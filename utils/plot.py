import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


# plot data                ----------------------------------------------------------------
def top_n_payment_dates_plot(payment_schedule_backend_table, top_n=5):
    
    main_observations = list(
        (
            payment_schedule_backend_table["payment_date"]
            .value_counts()
            .nlargest(top_n)
            .index.sort_values()
        )
    )

    # Plot distribution
    plt.figure(figsize=(20, 5))

    ax = sns.histplot(payment_schedule_backend_table["payment_date"], kde=True, bins=31)
    sns.despine(top=True, right=True)

    # Ensure x-axis starts at 0
    plt.xlim(left=1)

    # Add centered annotations inside the bins for main observation days
    for date in main_observations:
        for patch in ax.patches:
            if patch.get_x() <= date < patch.get_x() + patch.get_width():
                height = patch.get_height()
                center_x = patch.get_x() + (patch.get_width() / 2)  # Center text in the bin
                plt.text(center_x, 
                         height - 50,  # Adjust vertical position slightly above the bin
                         str(date), 
                         ha="center",
                         va="bottom", 
                         fontsize=12, 
                         color="black", 
                         fontweight="bold")

    # Calculate quantiles
    q25, q50, q75 = payment_schedule_backend_table["payment_date"].quantile([0.25, 0.5, 0.75])

    for quantile, label in zip([q25, q50, q75], ["25%", "50%", "75%"]):
        for patch in ax.patches:
            if patch.get_x() <= quantile < patch.get_x() + patch.get_width():
                height = patch.get_height()
                center_x = patch.get_x() + (patch.get_width() / 2)  # Center text in the bin
                plt.text(center_x, 
                         height + 1,  # Place slightly above the highest bin
                         label, 
                         ha="center", 
                         fontsize=12, 
                         color="black", 
                         fontweight="bold")

    plt.xlabel("Payment Date")
    plt.ylabel("Frequency")
    plt.title("Distribution of Payment Dates")
    plt.show()

def top_n_allowances_plot(allowance_events, top_n=5):
    
    main_observations = list(
        (
            allowance_events["allowance.amount"]
            .value_counts()
            .nlargest(top_n)
            .index.sort_values()
        )
    )

    # Plot distribution
    plt.figure(figsize=(20, 5))
    ax = sns.histplot(allowance_events["allowance.amount"], 
                      kde=True, 
                      bins=allowance_events["allowance.amount"].unique().size)
    
    # Remove top and right plot borders
    sns.despine(top=True, right=True)

    # Ensure x-axis starts at 0
    plt.xlim(left=0)

    # Adjust y-axis limit to ensure space for annotations
    y_max = ax.get_ylim()[1] * 1.1  # Increase by 10% for better spacing
    plt.ylim(top=y_max)

    # Add annotations inside the bins for main observation allowance amounts
    for idx, val in enumerate(main_observations):
        max_bin_height = max([patch.get_height() for patch in ax.patches if patch.get_x() <= val < patch.get_x() + patch.get_width()], default=0)
        plt.text(val + 1, 
                 max_bin_height + (y_max * 0.04),  # Offset text above the bin
                 f"{val:.0f}\nUSD", 
                 ha="center",
                 va="bottom", 
                 fontsize=12, 
                 color="black", 
                 fontweight="bold")

    # Calculate quantiles
    q25, q50, q75 = allowance_events["allowance.amount"].quantile([0.25, 0.5, 0.75])

    for quantile, label in zip([q25, q50, q75], ["25%", "50%", "75%"]):
        max_bin_height = max([patch.get_height() for patch in ax.patches if patch.get_x() <= quantile < patch.get_x() + patch.get_width()], default=0)
        plt.text(quantile + 1, 
                 max_bin_height + 10, #- (y_max * 0.1),  # Offset text above the bin
                 label, 
                 ha="center", 
                 fontsize=10, 
                 color="black")

    plt.xlabel("Allowance Amount (USD)")
    plt.ylabel("Frequency")
    plt.title("Distribution of Allowance Amount")
    plt.show()

def plot_categorical_variables(allowance_events):
    fig, axes = plt.subplots(1, 2, figsize=(15, 5))

    # Frequency Plot
    sns.countplot(
        y="allowance.scheduled.frequency",
        data=allowance_events,
        order=allowance_events["allowance.scheduled.frequency"].value_counts().index,
        ax=axes[0],
        palette="Blues_r",
        hue="allowance.scheduled.frequency", 
        legend=False  
    )
    axes[0].set_title("Allowance Frequency Distribution")
    axes[0].set_xlabel("Count")
    axes[0].set_ylabel("Frequency")
    sns.despine(left=True, bottom=True)

    # Annotate frequency bars
    for p in axes[0].patches:
        axes[0].annotate(f"{p.get_width():,.0f}", (p.get_width() + 2, p.get_y() + 0.4), fontsize=12, color="black")

    # Define ordered weekdays
    weekdays_order = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday", "daily"]

    # Day Plot
    sns.countplot(
        y="allowance.scheduled.day",
        data=allowance_events,
        order=[day for day in weekdays_order if day in allowance_events["allowance.scheduled.day"].unique()],
        ax=axes[1],
        palette="Greens_r",
        hue="allowance.scheduled.day", 
        legend=False  
    )
    axes[1].set_title("Allowance Scheduled Day Distribution")
    axes[1].set_xlabel("Count")
    axes[1].set_ylabel("Day")
    sns.despine(left=True, bottom=True)

    # Annotate day bars
    for p in axes[1].patches:
        axes[1].annotate(f"{p.get_width():,.0f}", (p.get_width() + 2, p.get_y() + 0.4), fontsize=12, color="black")

    plt.tight_layout()
    plt.show()

def plot_contingency_table(allowance_events):
    # Create the contingency table
    contingency_table = pd.crosstab(
        allowance_events["allowance.scheduled.day"], 
        allowance_events["allowance.scheduled.frequency"]
    )

    # Plot the heatmap
    plt.figure(figsize=(10, 6))
    ax = sns.heatmap(contingency_table, annot=True, cmap="Blues", fmt="d", linewidths=0.5)

    # Titles and labels
    plt.title("Contingency Table: Allowance Scheduled Frequency vs Day")
    plt.xlabel("Frequency")
    plt.ylabel("Day")

    plt.show()

def plot_frequency_and_errors(check_field_df):
    # Define order of frequencies
    frequency_order = ["biweekly", "weekly", "daily", "monthly"]

    fig, axes = plt.subplots(1, 2, figsize=(15, 6))

    # Frequency Plot (Original)
    sns.countplot(
        y="frequency_og",
        data=check_field_df,
        order=frequency_order,
        ax=axes[0],
        palette="Blues_r"
    )
    axes[0].set_title("Original Allowance Frequency Distribution")
    axes[0].set_xlabel("Count")
    axes[0].set_ylabel("Frequency")

    # Count total occurrences per frequency
    total_counts = check_field_df["frequency_og"].value_counts().reindex(frequency_order, fill_value=0).to_dict()

    # Annotate bars with count values
    for p in axes[0].patches:
        count = int(p.get_width()) if not pd.isna(p.get_width()) else 0
        axes[0].annotate(f"{count:,}", (p.get_width() + 2, p.get_y() + 0.4), fontsize=12, color="black")

    # Errors in next_payment_day by frequency
    error_df = check_field_df[check_field_df['next_payment_day_og'] != check_field_df['next_payment_day_updated']]
    errors_per_frequency = error_df["frequency_og"].value_counts().reindex(frequency_order, fill_value=0)

    # Calculate error percentage
    error_percentage = {freq: (errors_per_frequency[freq] / total_counts[freq] * 100) if total_counts[freq] > 0 else 0 for freq in frequency_order}

    # Create a DataFrame for plotting errors
    errors_df = pd.DataFrame({"frequency_og": frequency_order, "error_count": errors_per_frequency.values})

    sns.barplot(
        y="frequency_og",
        x="error_count",
        data=errors_df,
        order=frequency_order,
        palette="Reds_r",
        ax=axes[1]
    )
    axes[1].set_title("Errors Concentration by Frequency")
    axes[1].set_xlabel("Error Count")
    axes[1].set_ylabel("Frequency")

    # Annotate bars with error percentage
    for p in axes[1].patches:
        count = int(p.get_width()) if not pd.isna(p.get_width()) else 0
        freq = p.get_y() + 0.4  # Get corresponding frequency
        percentage = error_percentage.get(frequency_order[int(freq)], 0) if int(freq) < len(frequency_order) else 0
        axes[1].annotate(f"{count:,}\n{percentage:.1f}%", (p.get_width() + 2, p.get_y() + 0.4), fontsize=12, color="black")

    # Ensure both y-axes are equal
    axes[1].set_ylim(axes[0].get_ylim())

    plt.tight_layout()
    plt.show()
