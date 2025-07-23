import wikipedia

def get_context_from_wikipedia(query):
    """
    Fetches context from Wikipedia for a given query by combining summaries
    from the top search results.
    """
    try:
        search_results = wikipedia.search(query)
        if not search_results:
            print(f"No Wikipedia search results found for: '{query}'")
            return ""

        combined_context = []
        # Iterate through the top 5 search results to gather more comprehensive context.
        # This increases the chance of finding the correct answer.
        for i, title in enumerate(search_results[:5]): # Consider top 5 results
            try:
                # Fetch a concise summary (e.g., 5 sentences) for each potential relevant page.
                # Keeping individual summaries concise helps manage overall context length.
                summary = wikipedia.summary(title, sentences=5)
                if summary: # Only add non-empty summaries
                    combined_context.append(summary)
            except wikipedia.exceptions.DisambiguationError as e:
                # Handle cases where a search result title is ambiguous (e.g., "Java" could be many things)
                print(f"Wikipedia disambiguation error for '{title}': {e.options}. Skipping this title.")
                continue # Skip this title if it's ambiguous
            except wikipedia.exceptions.PageError:
                # Handle cases where the page for a given title does not exist
                print(f"Wikipedia page not found for title: '{title}'. Skipping this title.")
                continue # Skip if page doesn't exist
            except Exception as e:
                # Catch any other unexpected errors during summary fetching for a specific title
                print(f"Error fetching summary for '{title}': {e}. Skipping this title.")
                continue

        # Join the collected summaries into a single string.
        # Add a clear separator (e.g., " --- ") to distinguish content from different pages.
        full_context = " --- ".join(combined_context)

        # Implement a rough truncation to prevent the context from becoming too long
        # for the QA model. Most BERT-like models have a max token limit (e.g., 512 tokens).
        # 2000 characters is a rough estimate to stay within typical limits for a few summaries.
        if len(full_context) > 2000: # Slightly increased max context length
            full_context = full_context[:2000] + "..." # Truncate and add ellipsis

        if not full_context.strip(): # Check if context is empty after stripping whitespace
            print("No relevant context could be constructed from Wikipedia search results.")
            return "Sorry, no relevant context could be retrieved from Wikipedia."

        # print(f"Generated context length: {len(full_context)} characters") # Debugging
        return full_context

    except Exception as e:
        # Catch any top-level errors during the entire Wikipedia fetching process
        print(f"Overall Wikipedia fetching error: {e}")
        return "Sorry, an error occurred while trying to fetch information from Wikipedia."