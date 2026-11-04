
import { Users } from 'lucide-react';

const accounts = [
  {
    name: 'Soumyajit Mandal',
    email: 'admin@example.com',
    role: 'Admin',
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
      aria-label="EcoCollect demonstration accounts"
    >
      <div className="demo-accounts-heading">
        <Users size={18} />
        <div>
          <h3>Meet the EcoCollect team</h3>
          <p>Explore EcoCollect using our demonstration accounts.</p>
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

