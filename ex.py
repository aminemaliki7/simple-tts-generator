import pandas as pd

# Create a list of dictionaries with all the YouTube video ideas data
youtube_ideas = [
  {
        "Title": "Video 1: Why You're Overwhelmed (and What Actually Helps)",
        "Subject": "Overwhelm & Mental Load",
        "Main Idea 1": "Too many choices, too little clarity",
        "Main Idea 2": "The myth of multitasking",
        "Main Idea 3": "Tools to simplify your mental load",
        "Summary": "Modern overwhelm stems from excessive options, ineffective multitasking, and the need for intentional mental space creation.",
        "Description": "Feeling overwhelmed isn't a personal failure—it's a system failure. Let's fix that, one mindset shift at a time.",
        "City": "New York, USA"
    },
    {
        "Title": "Video 2: The Silent Productivity Killer: How Notification Anxiety Drains Your Energy",
        "Subject": "Digital Wellness",
        "Main Idea 1": "Notifications trigger stress responses",
        "Main Idea 2": "Constant alerts fragment thinking",
        "Main Idea 3": "Creating a notification strategy",
        "Summary": "Notification overload creates anxiety, fragments your focus, and requires a strategic approach to regain mental clarity.",
        "Description": "Every ping costs more than just a moment of attention. Discover why notifications are secretly exhausting you and how to take back control.",
        "City": "Tokyo, Japan"
    },
    {
        "Title": "Video 3: Digital Detox: Not Just a Trend, But a Survival Skill",
        "Subject": "Digital Boundaries",
        "Main Idea 1": "Screens are eating our lives",
        "Main Idea 2": "The science of digital addiction",
        "Main Idea 3": "How to unplug without losing touch",
        "Summary": "Screen consumption has moved beyond entertainment to addiction, requiring science-based strategies for meaningful disconnection.",
        "Description": "Disconnecting isn't about being a luddite—it's about being free. Here's how to take back your time and sanity.",
        "City": "Copenhagen, Denmark"
    },
    {
        "Title": "Video 4: Rebuilding Your Attention Span After Years of Scrolling",
        "Subject": "Attention & Focus",
        "Main Idea 1": "Scrolling rewired your brain",
        "Main Idea 2": "Attention is a trainable muscle",
        "Main Idea 3": "Progressive attention building exercises",
        "Summary": "Digital scrolling has neurologically altered our brains, but attention capacity can be strengthened through targeted, progressive mental exercises.",
        "Description": "Can't focus on books or long tasks anymore? Your attention span can be recovered. Here's a step-by-step guide to rebuild your focus after years of digital fragmentation.",
        "City": "Amsterdam, Netherlands"
    },
    {
        "Title": "Video 5: The Comparison Trap: Breaking Free from Social Media Anxiety",
        "Subject": "Social Media Wellness",
        "Main Idea 1": "Why our brains seek comparison",
        "Main Idea 2": "Social media creates false benchmarks",
        "Main Idea 3": "Practical steps to reset expectations",
        "Summary": "Our neurological tendency toward social comparison is intensified by unrealistic social media standards, requiring deliberate expectation recalibration.",
        "Description": "Everyone seems more successful, happy, and fulfilled online. Here's how to recognize the illusion and free yourself from the endless comparison cycle.",
        "City": "Melbourne, Australia"
    },
    {
        "Title": "Video 6: Why You're Never Satisfied (and How to Feel Enough)",
        "Subject": "Self-Worth & Contentment",
        "Main Idea 1": "We chase more but feel less",
        "Main Idea 2": "The comparison trap of 2025",
        "Main Idea 3": "Redefining success from the inside out",
        "Summary": "Constant pursuit leaves us feeling empty, while comparison exacerbates dissatisfaction, necessitating an internal redefinition of success.",
        "Description": "In a world obsessed with progress, it's hard to feel enough. Here's how to stop the chase and start feeling full.",
        "City": "Vancouver, Canada"
    },
    {
        "Title": "Video 7: The Courage to Be Disliked: Finding Freedom from Others' Opinions",
        "Subject": "Authenticity",
        "Main Idea 1": "People-pleasing is a prison",
        "Main Idea 2": "Why we fear judgment so deeply",
        "Main Idea 3": "Building approval independence",
        "Summary": "People-pleasing creates a psychological prison fueled by our deep-seated fear of judgment, requiring deliberate steps toward approval independence.",
        "Description": "Living for likes and approval is exhausting. This video shows how to break free from the need to please everyone and live authentically, even when it means being disliked.",
        "City": "Berlin, Germany"
    },
    {
        "Title": "Video 8: Money Anxiety in 2025: How to Breathe Again",
        "Subject": "Financial Wellness",
        "Main Idea 1": "Cost of living keeps rising",
        "Main Idea 2": "Financial fear is constant",
        "Main Idea 3": "Ways to feel secure without being rich",
        "Summary": "Economic pressures create persistent financial anxiety, requiring practical approaches to security regardless of income level.",
        "Description": "Money stress is at an all-time high. Here's how to stay calm, take control, and find peace no matter your income.",
        "City": "Toronto, Canada"
    },
    {
        "Title": "Video 9: Decision Fatigue: Why Simple Choices Feel Impossible in 2025",
        "Subject": "Decision Making",
        "Main Idea 1": "Modern life requires too many decisions",
        "Main Idea 2": "Your willpower is a finite resource",
        "Main Idea 3": "Decision minimalism techniques",
        "Summary": "The overwhelming number of daily decisions depletes your mental energy, proving willpower is limited and making decision minimalism essential.",
        "Description": "Can't decide what to watch, wear, or eat? You're not indecisive—you're experiencing decision fatigue. Here's how to preserve your mental energy for what matters.",
        "City": "Paris, France"
    },
    {
        "Title": "Video 10: The Power of Micro-Habits: Tiny Changes with Massive Results",
        "Subject": "Habit Formation",
        "Main Idea 1": "Small habits beat massive changes",
        "Main Idea 2": "The compound effect of daily actions",
        "Main Idea 3": "Building a system of micro-habits",
        "Summary": "Modest habits consistently outperform dramatic changes through the power of daily compounding, creating transformative systems for long-term success.",
        "Description": "Forget dramatic life overhauls. This video reveals how tiny, consistent actions create powerful change through the magic of compounding.",
        "City": "Lisbon, Portugal"
    },
    {
        "Title": "Video 11: The Morning Routine Myth: Finding What Actually Works for You",
        "Subject": "Productivity",
        "Main Idea 1": "Cookie-cutter routines don't work",
        "Main Idea 2": "Energy management vs. time management",
        "Main Idea 3": "Building a personalized morning practice",
        "Summary": "Generic morning routines fail because they prioritize rigid time management over energy optimization, necessitating individually tailored practices.",
        "Description": "5AM club, meditation, cold plunges—morning routine advice is everywhere. This video helps you cut through the noise and create a morning that actually serves YOUR life.",
        "City": "Portland, USA"
    },
    {
        "Title": "Video 12: The Lost Art of Rest: Why True Downtime Feels Impossible",
        "Subject": "Rest & Relaxation",
        "Main Idea 1": "Rest has been corrupted by productivity",
        "Main Idea 2": "Different types of rest we need",
        "Main Idea 3": "Creating guilt-free downtime",
        "Summary": "Our concept of rest has been contaminated by productivity culture, obscuring our diverse rest needs and making guilt-free downtime a necessary skill.",
        "Description": "Even our rest feels productive now—learning, optimizing, achieving. Learn how to embrace true, purposeless rest and why it's essential for your wellbeing.",
        "City": "Oslo, Norway"
    },
    {
        "Title": "Video 13: The Loneliness Epidemic: Why We Feel Alone in 2025",
        "Subject": "Loneliness & Connection",
        "Main Idea 1": "Modern life is isolating",
        "Main Idea 2": "Social media isn't real connection",
        "Main Idea 3": "How to rebuild community, offline",
        "Summary": "Our modern lifestyle creates isolation despite digital connection, requiring intentional offline community building.",
        "Description": "Loneliness is the quiet crisis of our time. Let's talk about why it's happening and what you can do to feel truly connected again.",
        "City": "Dublin, Ireland"
    },
    {
        "Title": "Video 14: How to Build Deep Relationships in a World of Shallow Connections",
        "Subject": "Relationships",
        "Main Idea 1": "Quantity replaced quality in relationships",
        "Main Idea 2": "Vulnerability creates genuine bonds",
        "Main Idea 3": "Practical steps to deepen connections",
        "Summary": "Modern relationships prioritize quantity over depth, while real connection requires vulnerability and intentional practices to cultivate meaningful bonds.",
        "Description": "With thousands of 'friends' online, why do we feel so disconnected? Learn how to cultivate fewer but deeper relationships that actually fulfill you.",
        "City": "Copenhagen, Denmark"
    },
    {
        "Title": "Video 15: How to Set Boundaries Without Feeling Guilty",
        "Subject": "Boundaries",
        "Main Idea 1": "2025 is full of emotional labor",
        "Main Idea 2": "Why saying no feels wrong",
        "Main Idea 3": "Scripts for kind but clear boundaries",
        "Summary": "Increasing emotional demands make boundaries essential, despite guilt, using compassionate but firm communication techniques.",
        "Description": "Protecting your peace doesn't make you selfish. Learn how to say no with love and mean it.",
        "City": "Austin, USA"
    },
    {
        "Title": "Video 16: How to Have Difficult Conversations in a Polarized World",
        "Subject": "Communication",
        "Main Idea 1": "Disagreement doesn't equal disrespect",
        "Main Idea 2": "Techniques for non-confrontational dialogue",
        "Main Idea 3": "Finding common ground deliberately",
        "Summary": "Productive disagreement can exist without disrespect when using non-confrontational dialogue techniques and intentionally seeking points of connection.",
        "Description": "In our divided world, difficult conversations feel impossible. This video offers practical tools to discuss tough topics without burning bridges.",
        "City": "Montreal, Canada"
    },
    {
        "Title": "Video 17: The New Self-Care: Beyond Bubble Baths to Actual Healing",
        "Subject": "Holistic Self-Care",
        "Main Idea 1": "True self-care isn't always pleasant",
        "Main Idea 2": "Addressing root causes vs. symptoms",
        "Main Idea 3": "Building a personalized healing routine",
        "Summary": "Authentic self-care often involves challenging work that addresses root causes rather than symptoms, requiring personalized healing practices beyond superficial indulgences.",
        "Description": "Self-care has been commercialized into superficial treats. This video redefines what actually fills your cup versus what just looks good on Instagram.",
        "City": "Bali, Indonesia"
    },
    {
        "Title": "Video 18: Finding Purpose When Traditional Paths Are Disappearing",
        "Subject": "Purpose & Meaning",
        "Main Idea 1": "Career ladders are dissolving",
        "Main Idea 2": "Purpose beyond occupation",
        "Main Idea 3": "Creating meaning in uncertainty",
        "Summary": "As traditional career trajectories disappear, finding purpose requires looking beyond occupation and developing techniques for creating meaning amid uncertainty.",
        "Description": "With traditional career paths and institutions changing rapidly, how do you find direction? Here's how to create purpose in a world where the old roadmaps no longer apply.",
        "City": "Seattle, USA"
    },
    {
        "Title": "Video 19: The Myth of Perfect Balance: A New Approach to Work and Life",
        "Subject": "Work-Life Harmony",
        "Main Idea 1": "Work-life balance is an impossible ideal",
        "Main Idea 2": "Seasons and rhythms vs. daily balance",
        "Main Idea 3": "Finding harmony instead of balance",
        "Summary": "Perfect work-life balance is an unattainable myth that ignores life's natural seasons and rhythms, suggesting harmony as a healthier alternative.",
        "Description": "Stop chasing perfect balance and start embracing the natural ebbs and flows of life. Here's a more realistic approach to managing work, rest, and everything in between.",
        "City": "Kyoto, Japan"
    },
    {
        "Title": "Video 20: Slow Living in a Fast World: Practical Steps for 2025",
        "Subject": "Slow Living",
        "Main Idea 1": "Speed as a modern addiction",
        "Main Idea 2": "The counterintuitive benefits of slowing down",
        "Main Idea 3": "Implementing slow living principles daily",
        "Summary": "Our societal addiction to speed masks the paradoxical advantages of deliberately slowing down and adopting daily slow living practices.",
        "Description": "In a world that demands speed, slowing down is revolutionary. Discover how to incorporate slow living principles into your life without dropping out of society.",
        "City": "Chiang Mai, Thailand"
    }
]

# Convert list of dictionaries to pandas DataFrame
df = pd.DataFrame(youtube_ideas)

# Define the column order
columns = ["Title", "Main Idea 1", "Main Idea 2", "Main Idea 3", "Summary", "Description", "City"]
df = df[columns]

# Create Excel writer object
excel_file = "20_YouTube_Ideas_with_Cities_2025.xlsx"
with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
    # Write DataFrame to Excel
    df.to_excel(writer, sheet_name='YouTube Ideas', index=False)
    
    # Get the workbook and the worksheet
    workbook = writer.book
    worksheet = writer.sheets['YouTube Ideas']
    
    # Auto-adjust columns' width
    for column in worksheet.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2)
        worksheet.column_dimensions[column_letter].width = adjusted_width

print(f"Excel file '{excel_file}' has been created successfully!")