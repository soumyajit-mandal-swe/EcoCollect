
import { Users } from 'lucide-react';

const teamMembers = [
  'Soumyajit Mandal',
  'Sourja Sinha',
  'Harsh Kumar Jha',
  'Sayandip Rout',
  'Aditya Chaubey',
];

const accounts = [
  {
    name: 'Soumyajit Mandal',
    email: 'admin@example.com',
    role: 'Admin',
  },
  {
    name: 'Soumyajit Mandal',
    email: 'soumyajit@example.com',
    role: 'User',
  },
  {
    name: 'Sourja Sinha',
    email: 'sourja@example.com',
    role: 'User',
  },
  {
    name: 'Harsh Kumar Jha',
    email: 'harsh@example.com',
    role: 'User',
  },
];

export default function DemoAccounts() {
  return (
    <section
      className="demo-accounts"
      aria-label="EcoCollect team and demo accounts"
    >
      <div className="demo-accounts-heading">
        <Users size={18} />
        <div>
          <h3>Meet the EcoCollect Team</h3>
          <p>Our DBMS mini-project team members.</p>
        </div>
      </div>

      <ul>
        {teamMembers.map((name) => (
          <li key={name}>
            <span>
              <strong>{name}</strong>
            </span>
            <span className="demo-role">
              Member
            </span>
          </li>
        ))}
      </ul>

      <div className="demo-accounts-heading">
        <Users size={18} />
        <div>
          <h3>Demo Login Accounts</h3>
          <p>Use one of these accounts to explore EcoCollect.</p>
        </div>
      </div>

      <ul>
        {accounts.map((account) => (
          <li key={account.email}>
            <span>
              <strong>{account.name}</strong>
              <span className="demo-email">
                {account.email}
              </span>
            </span>

            <span
              className={`demo-role ${
                account.role === 'Admin' ? 'demo-admin' : ''
              }`}
            >
              {account.role}
            </span>
          </li>
        ))}
      </ul>
    </section>
  );
}
