#!/usr/bin/env python3

import subprocess
import tempfile
import yaml
from jinja2 import Template


context = {
    "docker_tag_name": "v1.27.0_sunet-${GIT_COMMIT}",
    "branch_name": "v1.27.0",
    "repository_url": "https://github.com/Uninett/Argus.git"
}


def get_commit():
    # Capture the most recent commit hash using `git log --show-signature -1`
    result = subprocess.run(
        "git log --show-signature -1",
        shell=True,
        check=True,
        capture_output=True,
        text=True,
    )

    # Extract the commit hash from the git log output
    git_commit = None
    for line in result.stdout.splitlines():
        if line.startswith("commit"):
            git_commit = line.split()[1]  # Commit hash is the second word
            break
    return git_commit


def get_template(filename=".jenkins.yaml.jinja"):
    template_content = None
    # Read the Jinja2 template YAML file
    with open(filename, "r") as template_file:
        template_content = template_file.read()
        
    return template_content

# Use Python's tempfile module to create a temporary directory in memory
with tempfile.TemporaryDirectory() as temp_dir:
    # Clone the repository with --bare to save bandwidth
    subprocess.run(
        f"git clone --bare {context['repository_url']} {temp_dir} > /dev/null 2>&1",
        shell=True,
        check=True,
    )

    # Run the 'git for-each-ref' command to get the tags sorted by date
    result = subprocess.run(
        f"git -C {temp_dir} for-each-ref --sort=-creatordate --format '%(refname:short)' refs/tags",
        shell=True,
        check=True,
        capture_output=True,
        text=True,
    )

    # Split the output into a list of tags
    tags = result.stdout.splitlines()
    len_tags = len(tags)

    # Print the tags
    print(f"Tags from {context['repository_url']} listed by creation date:")
    for index, tag in enumerate(tags):
        print(f"{index+1}. {tag}")

    tag_number = input("Choose the tag you want to build: ")
    tag_number = int(tag_number)
    assert (
        tag_number >= 1 and tag_number <= len_tags + 1
    ), "The number should be one in the list above"
    print(f"You have choosed: {tag_number}, {tags[tag_number-1]}")
    git_commit = get_commit()[:8]
    context['branch_name'] = tags[tag_number-1]
    context['docker_tag_name'] = f"{tags[tag_number-1]}_sunet-" + "${GIT_COMMIT}"
    
    # Todo. change .jenkins.yaml with the new version
    template = Template(get_template(filename="templates/.jenkins.yaml.jinja"))
    rendered_yaml = template.render(context)
    yaml_data = yaml.safe_load(rendered_yaml)
    # Print the rendered YAML content
    print("Updated .jenkins.yaml:\n")
    yaml_output = yaml.dump(yaml_data, default_flow_style=False)
    tabbed_yaml_output = "\n".join(f"\t{line}" for line in yaml_output.splitlines())
    print(tabbed_yaml_output)

    # TODOD. push changes to git
    file_to_remplace = ".jenkins.yaml"
    with open(file_to_remplace, "w") as output_file:
        output_file.write(rendered_yaml)
    
    # Prompt the user for a commit message
    commit_message = input("Enter the commit message: ")

    print("\tCommitting changes...")
    # Commit the changes
    subprocess.run('git add .jenkins.yaml', shell=True, check=True)
    subprocess.run(f'git commit -m "{commit_message}"', shell=True, check=True)
        
    print("pushing changes to repository...")
    subprocess.run("git push -u origin main", shell=True, check=True)
