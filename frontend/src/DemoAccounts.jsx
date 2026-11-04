import { Users } from 'lucide-react';

const accounts = [
  { name: 'Romit Singh', email: 'admin@example.com', role: 'Admin' },
  { name: 'Soumyajit Mandal', email: 'soumyajit@example.com', role: 'User' },
  { name: 'Sourja Sinha', email: 'sourja@example.com', role: 'User' },
  { name: 'Harsh Kumar Jha', email: 'harsh@example.com', role: 'User' },
  { name: 'Sayandip Rout', email: 'sayandip@example.com', role: 'User' },
  { name: 'Aditya Chaubey', email: 'aditya@example.com', role: 'User' },
];

export default function DemoAccounts() {
  return <section className="demo-accounts" aria-label="Group demonstration accounts">
    <div className="demo-accounts-heading"><Users size={18} /><div><h3>Meet the EcoCollect team</h3><p>Use a group account to explore the local demo.</p></div></div>
    <ul>{accounts.map(account => <li key={account.email}>
      <span><strong>{account.name}</strong><span className="demo-email">{account.email}</span></span>
      <span className={`demo-role ${account.role === 'Admin' ? 'demo-admin' : ''}`}>{account.role}</span>
    </li>)}</ul>
    <div className="demo-passwords"><span>Admin password <code>EcoAdmin123!</code></span><span>User password <code>EcoUser123!</code></span></div>
  </section>;
}
