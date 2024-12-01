context_extractor_prompt = """
You are part of a team tasked with generating role-aware and context-aware image alt texts for images on websites. Your role is to summarize the context of the website in which the image appears to help generate the most suitable alt text for the image. Extract all relevant information from the website, such as the names of relevant organizations, the purpose of the website, the type of content, and any other relevant details that can help determine the context of the image. Do not make up any information; only use the information provided in the website.

Text:
{message}

"""

# role_identifier_prompt = """
# You are part of a team tasked with generating role-aware and context-aware image alt texts for images on websites. Your role is to identify the role of the given image in the website according to the definitions provided by the WCAG Web Accessibility Initiative (WAI) outlined below.


# 1. Informative: Images that graphically represent concepts and information, typically pictures, photos, and illustrations. The text alternative should be at least a short description conveying the essential information presented by the image.

# 2. Decorative: Provide a null text alternative (alt="") when the only purpose of an image is to add visual decoration to the page, rather than to convey information that is important to understanding the page. 

# 3. Functional: The text alternative of an image used as a link or as a button should describe the functionality of the link or button rather than the visual image. Examples of such images are a printer icon to represent the print function or a button to submit a form.

# 4. Complex: To convey data or detailed information, provide a complete text equivalent of the data or information provided in the image as the text alternative.


# As each role needs to be handled differently when generating alt texts, your output will be used to help another team member write the most suitable alt text that is role-aware and contex-aware for the image to help create more accessible websites.

# {message}

# Return only the role of the image from the list above. Return the role as a single word without any enclosing bracket, e.g., informative, decorative, functional, text, or complex. THIS IS IMPORTANT! RETURN ONLY THE ROLE OF THE IMAGE.
# """

role_identifier_prompt = """
You are part of a team tasked with generating role-aware and context-aware image alt texts for images on websites. Your role is to identify the role of the given image in the website according to the definitions provided by the WCAG Web Accessibility Initiative (WAI) outlined below.


1. informative: Images that graphically represent concepts and information, typically pictures, photos, and illustrations. The text alternative should be at least a short description conveying the essential information presented by the image.

2. decorative: The only purpose of an image is to add visual decoration to the page, rather than to convey information that is important to understanding the page. This includes images that are considered eye candy or used for visual effect. Classify the image to decorative if having a null alt-text (alt="") will not result in any loss of information.

3. functional: Images used as a link or as a button, which carry a functionality to the page. Examples of such images are a printer icon to represent the print function or a button to submit a form. The alt text should describe the functionality of the link or button rather than the visual image.

4. complex: Images used to convey data or detailed information, such as graphs or charts. Alt texts provide a complete text equivalent of the data or information provided in the image as the text alternative.


As each role needs to be handled differently when generating alt texts, your output will be used to help another team member write the most suitable alt text that is role-aware and contex-aware for the image to help create more accessible websites.

Return only the role of the image from the list above. Return the role as a single word without any enclosing bracket, e.g., informative, decorative, functional, text, or complex. THIS IS IMPORTANT! RETURN ONLY THE ROLE OF THE IMAGE.

{message}
"""


image_description_prompt = """
Describe the image in a few words to help identify its role. This description should be concise and capture the essence of the image. You can mention any text present in the image, the context in which the image appears, or any other relevant details that can help determine the role of the image.

{message}
"""


alt_text_prompts = {
    "informative": """
        The role of the image has been identified as 'informative'. Informative images convey a simple concept or information that can be expressed in a short phrase or sentence. The text alternative should convey the meaning or content that is displayed visually, which typically isn't a literal description of the image. In some situations a detailed literal description may be needed, but only when the content of the image is all or part of the conveyed information.

        Example 1: Images used to label other information
        This example includes two image icons - one of a telephone, one of a fax machine. A phone number follows each image. Consistent with the visual presentation, the text alternatives "Telephone:" and "Fax:" are used to identify the device associated with each number.

        Example 2: Images used to supplement other information
        The following example shows a dog wearing a bell. It supplements the adjacent text that explains the purpose of this bell (Off-duty guide dogs often wear a bell. Its ring helps the blind owner keep track of the dog's location). A short text alternative is sufficient to describe the information that is displayed visually but is not explained in the text; in this case, the text alternative is "Dog with a bell attached to its collar.".

        Example 3: Images conveying succinct information
        A simple diagram illustrates a counter-clockwise direction for unscrewing a bottle top or cap. The information can be described in a short sentence, so the text alternative "Push the cap down and turn it counter-clockwise (from right to left)" is given in the alt attribute.

        Example 4: Images conveying an impression or emotion
        A photograph shows a happy family group. It's a stock image so the individuals should not be identified. It's being used to give the impression that the website or the company it represents is family-friendly. The text alternative is "We're family-friendly" as this best describes the intended impression.

        Example 5: Images conveying file format
        In this example, a document is available to download in three different formats identified by format icons within text links. They have the text alternatives "HTML", "Word document", and "PDF" to distinguish the file type for each link.

        Write a concise and descriptive alt text for the image based on the role of the image as 'informative' as well as the context provided from the website. The alt text should convey the meaning or content of the image in a way that is meaningful and useful to those who rely on screen readers or other assistive technologies.

        Write only the alt text for the image. Do not include any additional information or context. Do not enclose the alt text in quotes. For example, if the alt text is "A dog with a bell attached to its collar.", you should only write: A dog with a bell attached to its collar.

        {message}

        """,
    
    "functional": """
        Functional images are used to initiate actions rather than to convey information. They are used in buttons, links, and other interactive elements. The text alternative for the image should convey the action that will be initiated (the purpose of the image), rather than a description of the image.

        For instance, as shown in examples below, the text alternative should be “print this page” rather than “(image of a) printer”, “search” rather than “magnifying lens” or “Example.com homepage” rather than “Example.com logo”.

        Example 1: Image used alone as a linked logo
        The following image of the W3C Logo is the only content of a link that leads to the W3C home page (no relevant next or previous text). It has the text alternative "W3C home" to indicate where the link will take the user.

        Example 2: Logo image within link text
        In this example, the W3C logo is used to supplement text within a link that leads to the W3C home page (next text is "W3C Home"). The image does not represent different functionality or convey other information than that already provided in the link text, so a null (empty) value is applied, (alt=""), to avoid redundancy and repetition. In effect the image is a decorative adjunct or visual cue to the link text.

        Example 3: Icon image conveying information within link text
        In this example, the image of a window icon follows text within a link to inform users that the link will open in a new window. It has the text alternative “new window” to convey the meaning of the icon: that activating the link will open a new browser window.

        Example 4: Stand-alone icon image that has a function
        The following image is an icon representing a printer to denote print functionality. It has the text alternative “Print this page” because its purpose is to activate the print dialog when it is selected.

        Example 5: Image used in a button
        The following image is used to give the button a distinct style. In this case, it is the button to initiate a search request and is an icon representing a magnifying lens. The text alternative for the image is “search” to convey the purpose of the button.

        Write a concise and descriptive alt text for the image based on the role of the image as 'functional' as well as the context provided from the website. The alt text should convey the action that will be initiated by the image (the purpose of the image) in a way that is meaningful and useful to those who rely on screen readers or other assistive technologies.

        Write only the alt text for the image. Do not include any additional information or context. Do not enclose the alt text in quotes. For example, if the alt text is "Print this page", you should only write: Print this page.

        {message}
    """,

    "text": """
        The role of the image has been identified as 'text'. Text images are those that contain readable text within the image itself. 

        When an image contains text that is important to understanding the content, the alt text should contain the same words as in the image. This ensures that the information is accessible to users who cannot see the image.

        Write a concise and descriptive alt text for the image based on the role of the image as 'functional' as well as the context provided from the website. The alt text should convey the action that will be initiated by the image (the purpose of the image) in a way that is meaningful and useful to those who rely on screen readers or other assistive technologies.

        Write only the alt text for the image. Do not include any additional information or context. Do not enclose the alt text in quotes. For example, if the alt text is "Print this page", you should only write: Print this page.

        {message}
    """,

    "complex": """
        The role of the image has been identified as 'complex'. Complex images are those that convey detailed information or data that cannot be easily described in a few words. 

        When an image contains complex information, the alt text should provide a complete text equivalent of the data or information presented in the image. This ensures that users who cannot see the image can still access the information it contains.

        Write a concise and descriptive alt text for the image based on the role of the image as 'functional' as well as the context provided from the website. The alt text should convey the action that will be initiated by the image (the purpose of the image) in a way that is meaningful and useful to those who rely on screen readers or other assistive technologies.

        Write only the alt text for the image. Do not include any additional information or context. Do not enclose the alt text in quotes. For example, if the alt text is "Print this page", you should only write: Print this page.

        {message}
    """,
}