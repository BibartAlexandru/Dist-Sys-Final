# Use case
- Network managed by Cisco Catalyst Center
- Poll network device configuration files from the Catalyst Center API and push changes (if any) to a GitHub repository
### Usage
- Clone the repository
- Get access to the Catalyst Center API
1. Getting access to Catalyst Center's API
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
- Use the credentials in https://devnetsandbox.cisco.com/DevNet/operation_hub > Right Click on the instance > Access Details > administrator/Cisco1234!
