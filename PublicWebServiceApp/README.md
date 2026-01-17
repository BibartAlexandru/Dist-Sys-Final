# Use case
- Network managed by Cisco Catalyst Center
- Poll network device configuration files from the Catalyst Center API and push changes (if any) to a GitHub repository

### Usage
- The instructions assume you're using a UNIX based OS. Commands will be shown for Arch Linux
- Clone the repository `git clone https://github.com/BibartAlexandru/Dist-Sys-Final.git`
- Install docker & docker compose `sudo pacman -Sy docker docker-compose`
- Get access to the Catalyst Center API (see further down)
- Create a GitHub fine-grained token that has Read access to `Metadata` and Read-Write access to `Code`
```bash
cd Dist-Sys-Final/PublicWebServiceApp/src
mv .env.example .env
vi env # Add your variables. https://${GITHUB_TOKEN}@github.com/${GITHUB_USER}/${GITHUB_REPO}.git will be accessed.
chmod +x ./re # This script is used to restart the container
chmod +x ./lg # This is used to print logs 
./re 
# Optionally check for the container stdout
./lg
```

###### Getting access to Catalyst Center's API
- Navigate to https://devnetsandbox.cisco.com/DevNet
- Create an account
- Click on "Catalyst Center Sandbox" > "Launch"
- After about 1 hour, the instance will be ready and you should receive an email with connection details
- Download Cisco Secure Client VPN from Cisco's website, or just follow the instructions in the email. On Arch Linux, you can `
#### Download procedure on Arch Linux
```
yay -Sy cisco-secure-client
sudo systemctl enable --now vpnagentd.service
sudo systemctl status vpnagentd.service
# Should be up at this point. Read more at: https://aur.archlinux.org/packages/cisco-secure-client
# And you can start it!
cisco-secure-client & disown
```
- Enter the Lab Network Address received in the email in the network field. Also enter your username and password. All these credentials were received in the email
- You can see details about the instance in the link from the email (Navigate there)
- Use the credentials for access to the API in https://devnetsandbox.cisco.com/DevNet/operation_hub > Right Click on the instance > Access Details > administrator/Cisco1234!
