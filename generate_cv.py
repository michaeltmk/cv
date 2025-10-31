#!/usr/bin/env python3
"""
CV Generator Script
Reads portfolio.yaml and generates a LaTeX CV document
"""

import yaml
import sys
from pathlib import Path
from datetime import datetime


def load_portfolio_data(yaml_path):
    """Load and parse the portfolio YAML file"""
    try:
        with open(yaml_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print(f"Error: Could not find {yaml_path}")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML: {e}")
        sys.exit(1)


def escape_latex(text):
    """Escape special LaTeX characters in text"""
    if not text:
        return ""
    
    # Replace special LaTeX characters
    # Don't escape backslashes that we introduce ourselves
    text = text.replace('&', r'\&')
    text = text.replace('%', r'\%')
    text = text.replace('$', r'\$')
    text = text.replace('#', r'\#')
    text = text.replace('^', r'\textasciicircum{}')
    text = text.replace('_', r'\_')
    text = text.replace('{', r'\{')
    text = text.replace('}', r'\}')
    text = text.replace('~', r'\textasciitilde{}')
    # Only escape backslashes that were originally in the text (not ones we added)
    # This is tricky, so let's avoid escaping backslashes for now
    
    return text


def format_description(description):
    """Format description to LaTeX itemize format"""
    if not description:
        return ""
    
    if isinstance(description, list):
        # If description is already a list, format each item
        formatted_items = []
        for item in description:
            # Clean up the item text
            clean_item = item.strip()
            if clean_item.startswith('–') or clean_item.startswith('-'):
                clean_item = clean_item[1:].strip()
            # Escape special LaTeX characters
            clean_item = escape_latex(clean_item)
            formatted_items.append(f"\\item[--] {clean_item}")
        return '\n        '.join(formatted_items)
    else:
        # Handle the old multiline string format (fallback)
        text = description.strip()
        
        # Split by em-dash (–) and regular dash (-) at the beginning of "lines"
        import re
        # Split on em-dash or dash that follows a space or is at the beginning
        parts = re.split(r'(?:^|(?<=\s))(?:–|-)(?=\s)', text)
        
        formatted_lines = []
        
        for i, part in enumerate(parts):
            part = part.strip()
            if not part:
                continue
                
            if i == 0 and not (text.startswith('–') or text.startswith('-')):
                # First part might not be a bullet if text doesn't start with dash
                formatted_lines.append(escape_latex(part))
            else:
                # This is a bullet point
                formatted_lines.append(f"\\item[--] {escape_latex(part)}")
        
        return '\n        '.join(formatted_lines)


def generate_experience_section(experiences):
    """Generate the work experience section"""
    if not experiences:
        return ""
    
    sections = []
    current_company = None
    
    for exp in experiences:
        company = exp.get('company', '')
        position = exp.get('position', '')
        period = exp.get('period', '')
        description = exp.get('description', '')
        skills = exp.get('Skills', [])  # Extract skills
        
        # Start new company section or continue with same company
        if company != current_company:
            if current_company is not None:
                sections.append("\\end{tabularx}\n")
            
            sections.append(f"""\\begin{{tabularx}}{{\\linewidth}}{{ @{{}}l r@{{}} }}
\\textbf{{{escape_latex(company)}, Hong Kong}} \\\\[3.75pt]""")
            current_company = company
        
        # Build the content with description and skills
        content_parts = []
        if description:
            content_parts.append(format_description(description))
        
        # Add skills if available
        if skills:
            if isinstance(skills, list):
                skills_str = ' · '.join(skills)
            else:
                skills_str = str(skills)
            content_parts.append(f"\\item[--] Skills: {escape_latex(skills_str)}")
        
        content = '\n        '.join(content_parts)
        
        # Add position
        sections.append(f"""\\textbf{{{escape_latex(position)}}} & \\hfill {escape_latex(period)} \\\\[3.75pt]
\\multicolumn{{2}}{{@{{}}X@{{}}}}{{
\\begin{{minipage}}[t]{{\\linewidth}}
    \\begin{{itemize}}[nosep,after=\\strut, leftmargin=1em, itemsep=3pt]
        {content}
    \\end{{itemize}}
\\end{{minipage}}
}}  \\\\""")
    
    # Close the last table
    if current_company is not None:
        sections.append("\\end{tabularx}")
    
    return '\n'.join(sections)


def generate_certifications_section(certifications):
    """Generate the certifications section"""
    if not certifications:
        return ""
    
    sections = []
    for cert in certifications:
        institution = cert.get('institution', '')
        degree = cert.get('degree', '')
        year = cert.get('year', '')
        description = cert.get('description', '')
        
        sections.append(f"""\\begin{{tabularx}}{{\\linewidth}}{{ @{{}}l r@{{}} }}
    \\textbf{{{escape_latex(degree)} — {escape_latex(institution)}}} & \\hfill {escape_latex(year)} \\\\[3.75pt]
    \\multicolumn{{2}}{{@{{}}X@{{}}}}{{DESCRIPTION_PLACEHOLDER}}
\\end{{tabularx}}""")
        
        # Replace placeholder with description
        if description:
            if isinstance(description, list):
                # Join list descriptions with periods
                description_text = '. '.join(description)
            else:
                description_text = description
            
            # Escape the description text first
            escaped_description = escape_latex(description_text)
            
            # Check if there's a link to add
            link = cert.get('link', {})
            if link and 'url' in link and 'text' in link:
                # Add hyperlink after the description
                link_url = link['url']
                link_text = escape_latex(link['text'])
                # Build the final text with properly formed LaTeX href command
                final_text = f"{escaped_description} Link: \\href{{{link_url}}}{{{link_text}}}"
            else:
                final_text = escaped_description
            
            sections[-1] = sections[-1].replace('DESCRIPTION_PLACEHOLDER', final_text)
        else:
            sections[-1] = sections[-1].replace('DESCRIPTION_PLACEHOLDER', '')
    
    return '\n\n'.join(sections)


def generate_projects_section(projects):
    """Generate the projects section"""
    if not projects:
        return ""
    
    sections = []
    for project in projects:
        title = project.get('title', '')
        description = project.get('description', '')
        tech_stack = project.get('tech_stack', [])
        repo_url = project.get('repo_url', '')
        demo_url = project.get('demo_url', '')
        start_date = project.get('start_date', '')
        end_date = project.get('end_date', '')
        
        # Format the period
        if start_date and end_date:
            period = f"{start_date} - {end_date}"
        elif start_date:
            period = f"{start_date} - Present"
        elif end_date:
            period = end_date
        else:
            period = "Present"  # Default fallback
        
        # Format tech stack
        tech_str = ' · '.join(tech_stack) if tech_stack else ''
        
        # Format URLs
        url_sections = []
        if repo_url:
            url_sections.append(f"Repository: \\url{{{repo_url}}}")
        if demo_url:
            url_sections.append(f"Demo: \\url{{{demo_url}}}")
        
        project_content = f"""\\begin{{tabularx}}{{\\linewidth}}{{ @{{}}l r@{{}} }}
\\textbf{{{escape_latex(title)}}} & \\hfill {escape_latex(period)} \\\\[3.75pt]
\\multicolumn{{2}}{{@{{}}X@{{}}}}{{
\\begin{{minipage}}[t]{{\\linewidth}}
    \\begin{{itemize}}[nosep,after=\\strut, leftmargin=1em, itemsep=3pt]"""
        
        # Handle description as array or string
        if isinstance(description, list):
            for desc_item in description:
                project_content += f"\n        \\item[] {escape_latex(desc_item)}"
        else:
            project_content += f"\n        \\item[] {escape_latex(description)}"
        
        if tech_str:
            project_content += f"\n        \\item[] Skills: {escape_latex(tech_str)}"
        
        # Add URLs
        for url_section in url_sections:
            project_content += f"\n        \\item[] {url_section}"
        
        project_content += """
    \\end{itemize}
\\end{minipage}
}
\\end{tabularx}"""
        
        sections.append(project_content)
    
    return '\n\n'.join(sections)


def generate_education_section(education):
    """Generate the education section"""
    if not education:
        return ""
    
    sections = []
    for edu in education:
        institution = edu.get('institution', '')
        degree = edu.get('degree', '')
        year = edu.get('year', '')
        
        sections.append(f"{escape_latex(year)} & {escape_latex(degree)} at \\textbf{{{escape_latex(institution)}}} \\\\")
    
    return '\n'.join(sections)


def generate_skills_section(skills):
    """Generate the skills section"""
    if not skills:
        return ""
    
    sections = []
    
    skill_mappings = {
        'programming_languages': 'Programming Languages',
        'data_software_technical_skills': 'Data \\& software Technical Skills',
        'ml_technical_skills': 'ML Technical Skills',
        'cloud_computing_technical_skills': 'Cloud Computing Technical Skills',
        'hardware_technical_skills': 'Hardware Technical Skills',
        'soft_skills': 'Soft Skills',
        'languages': 'Languages'
    }
    
    for key, label in skill_mappings.items():
        if key in skills and skills[key]:
            skill_list = skills[key]
            if isinstance(skill_list, list):
                skill_str = ', '.join(skill_list)
            else:
                skill_str = str(skill_list)
            
            sections.append(f"{label} & \\normalsize{{{escape_latex(skill_str)}}}\\\\")
    
    return '\n'.join(sections)


def generate_latex_cv(data):
    """Generate the complete LaTeX CV document"""
    
    # Extract data sections
    personal = data.get('personal', {})
    contact = data.get('contact', {})
    professional = data.get('professional', {})
    skills = data.get('skills', {})
    projects = data.get('projects', [])
    
    name = personal.get('name', 'Your Name')
    description = personal.get('description', '')
    
    # Contact information
    email = contact.get('email', '')
    social = contact.get('social', {})
    github_username = social.get('github', {}).get('username', '')
    linkedin_username = social.get('linkedin', {}).get('username', '')
    
    # Professional sections
    experiences = professional.get('experience', [])
    education = professional.get('education', [])
    certifications = professional.get('additional_education', [])
    
    # Generate sections
    experience_section = generate_experience_section(experiences)
    certifications_section = generate_certifications_section(certifications)
    projects_section = generate_projects_section(projects)
    education_section = generate_education_section(education)
    skills_section = generate_skills_section(skills)
    
    # Template
    latex_template = f"""%-----------------------------------------------------------------------------------------------------------------------------------------------%
%	The MIT License (MIT)
%
%	Copyright (c) 2021 Jitin Nair
%
%	Permission is hereby granted, free of charge, to any person obtaining a copy
%	of this software and associated documentation files (the "Software"), to deal
%	in the Software without restriction, including without limitation the rights
%	to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
%	copies of the Software, and to permit persons to whom the Software is
%	furnished to do so, subject to the following conditions:
%	
%	THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
%	IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
%	FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
%	AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
%	LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
%	OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
%	THE SOFTWARE.
%	
%
%-----------------------------------------------------------------------------------------------------------------------------------------------%

%----------------------------------------------------------------------------------------
%	DOCUMENT DEFINITION
%----------------------------------------------------------------------------------------

% article class because we want to fully customize the page and not use a cv template
\\documentclass[a4paper,12pt]{{article}}

%----------------------------------------------------------------------------------------
%	FONT
%----------------------------------------------------------------------------------------

% % fontspec allows you to use TTF/OTF fonts directly
% \\usepackage{{fontspec}}
% \\defaultfontfeatures{{Ligatures=TeX}}

% % modified for ShareLaTeX use
% \\setmainfont[
% SmallCapsFont = Fontin-SmallCaps.otf,
% BoldFont = Fontin-Bold.otf,
% ItalicFont = Fontin-Italic.otf
% ]
% {{Fontin.otf}}

%----------------------------------------------------------------------------------------
%	PACKAGES
%----------------------------------------------------------------------------------------
\\usepackage{{url}}
\\usepackage{{parskip}} 	

%other packages for formatting
\\RequirePackage{{color}}
\\RequirePackage{{graphicx}}
\\usepackage[usenames,dvipsnames]{{xcolor}}
\\usepackage[scale=0.9]{{geometry}}

%tabularx environment
\\usepackage{{tabularx}}

%for lists within experience section
\\usepackage{{enumitem}}

% centered version of 'X' col. type
\\newcolumntype{{C}}{{>{{\\centering\\arraybackslash}}X}} 

%to prevent spillover of tabular into next pages
\\usepackage{{supertabular}}
\\usepackage{{tabularx}}
\\newlength{{\\fullcollw}}
\\setlength{{\\fullcollw}}{{0.47\\textwidth}}

%custom \\section
\\usepackage{{titlesec}}				
\\usepackage{{multicol}}
\\usepackage{{multirow}}

%CV Sections inspired by: 
%http://stefano.italians.nl/archives/26
\\titleformat{{\\section}}{{\\Large\\scshape\\raggedright}}{{}}{{0em}}{{}}[\\titlerule]
\\titlespacing{{\\section}}{{0pt}}{{10pt}}{{10pt}}

%for publications
\\usepackage[style=authoryear,sorting=ynt, maxbibnames=2]{{biblatex}}

%Setup hyperref package, and colours for links
\\usepackage[unicode, draft=false]{{hyperref}}
\\definecolor{{linkcolour}}{{rgb}}{{0,0.2,0.6}}
\\hypersetup{{colorlinks,breaklinks,urlcolor=linkcolour,linkcolor=linkcolour}}
\\addbibresource{{citations.bib}}
\\setlength\\bibitemsep{{1em}}

%for social icons
\\usepackage{{fontawesome5}}

%debug page outer frames
%\\usepackage{{showframe}}

%----------------------------------------------------------------------------------------
%	BEGIN DOCUMENT
%----------------------------------------------------------------------------------------
\\begin{{document}}

% non-numbered pages
\\pagestyle{{empty}} 

%----------------------------------------------------------------------------------------
%	TITLE
%----------------------------------------------------------------------------------------

\\begin{{tabularx}}{{\\linewidth}}{{@{{}} C @{{}}}}
\\Huge{{{escape_latex(name)}}} \\\\[7.5pt]"""

    # Add contact information
    contact_parts = []
    if github_username:
        contact_parts.append(f"\\href{{https://github.com/{github_username}}}{{\\raisebox{{-0.05\\height}}\\faGithub\\ {github_username}}}")
    if linkedin_username:
        contact_parts.append(f"\\href{{https://linkedin.com/in/{linkedin_username}}}{{\\raisebox{{-0.05\\height}}\\faLinkedin\\ {linkedin_username}}}")
    if email:
        contact_parts.append(f"\\href{{mailto:{email}}}{{\\raisebox{{-0.05\\height}}\\faEnvelope\\ {email}}}")
    
    if contact_parts:
        latex_template += f"\n{' \\ $|$ \\ '.join(contact_parts)} \\\\"

    latex_template += """
\\end{tabularx}

%----------------------------------------------------------------------------------------
% EXPERIENCE SECTIONS
%----------------------------------------------------------------------------------------

%Interests/ Keywords/ Summary
\\section{Summary}"""

    if description:
        latex_template += f"\n{escape_latex(description)}"

    latex_template += f"""

%Experience
\\section{{Work Experience}}
{experience_section}"""

    if certifications_section:
        latex_template += f"""

%Certifications
\\section{{Certifications}}

{certifications_section}"""

    if projects_section:
        latex_template += f"""

%Projects
\\section{{Projects}}

{projects_section}"""

    latex_template += f"""

%----------------------------------------------------------------------------------------
%	EDUCATION
%----------------------------------------------------------------------------------------
\\section{{Education}}
\\begin{{tabularx}}{{\\linewidth}}{{@{{}}l X@{{}}}}	
{education_section}

\\end{{tabularx}}

%----------------------------------------------------------------------------------------
%	SKILLS
%----------------------------------------------------------------------------------------
\\section{{Skills}}
\\begin{{tabularx}}{{\\linewidth}}{{@{{}}l X@{{}}}}
{skills_section}
\\end{{tabularx}}

\\vfill
\\center{{\\footnotesize Last updated: \\today}}

\\end{{document}}"""

    return latex_template


def main():
    """Main function"""
    # Define paths
    script_dir = Path(__file__).parent
    yaml_path = script_dir / "portfolio.yaml"
    output_path = script_dir / "cv.tex"
    
    # Load portfolio data
    print(f"Loading portfolio data from {yaml_path}")
    data = load_portfolio_data(yaml_path)
    
    # Generate LaTeX CV
    print("Generating LaTeX CV...")
    latex_content = generate_latex_cv(data)
    
    # Write to file
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(latex_content)
    
    print(f"CV generated successfully: {output_path}")
    print(f"You can now compile it with: pdflatex {output_path}")


if __name__ == "__main__":
    main()
