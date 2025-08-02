# IOU Tracker Frontend

A modern, responsive Vue.js single-page application (SPA) for managing personal debts and "I Owe You" records. This frontend seamlessly integrates with a Django REST API backend to help users track who owes them money, who they owe money to, and manage related notifications.

## 🚀 Features

### Core Functionality
- **User Authentication**: Secure registration, login, and logout
- **IOU Management**: Create, view, edit, and delete IOUs
- **Debt Management**: Track formal debts separately from casual IOUs
- **Dashboard**: Overview of financial status with statistics and recent activity
- **Notifications**: Real-time updates on IOU and debt activities
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices

### Technical Features
- **Vue 3**: Modern Vue.js with Composition API
- **TypeScript**: Full type safety throughout the application
- **Pinia**: State management for authentication and data
- **Vue Router**: Client-side routing with protected routes
- **Tailwind CSS**: Utility-first CSS framework for rapid styling
- **Heroicons**: Beautiful SVG icons
- **Axios**: HTTP client for API communication

## 🛠️ Technology Stack

- **Frontend Framework**: Vue.js 3.4+
- **Language**: TypeScript
- **Build Tool**: Vite
- **State Management**: Pinia
- **Routing**: Vue Router 4
- **Styling**: Tailwind CSS 3
- **Icons**: Heroicons Vue
- **HTTP Client**: Axios
- **UI Components**: Headless UI Vue

## 📋 Prerequisites

Before running this application, ensure you have:

- Node.js 18+ installed
- npm or yarn package manager
- Django REST API backend running (see Backend Setup section)

## 🚀 Quick Start

### 1. Clone and Install

```bash
# Install dependencies
npm install

# Or using yarn
yarn install
```

### 2. Environment Setup

The application is configured to work with these default settings:

- **API Base URL**: `http://localhost:8000/api` (Django backend)
- **Frontend Port**: `3000` (Vite dev server)

You can modify these in the `.env` file if needed:

```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_APP_NAME=IOU Tracker
VITE_APP_VERSION=1.0.0
```

### 3. Start Development Server

```bash
# Start the development server
npm run dev

# Or using yarn
yarn dev
```

The application will be available at `http://localhost:3000`

### 4. Backend Setup

This frontend requires a Django REST API backend. The expected API endpoints are:

#### Authentication Endpoints
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login  
- `POST /api/auth/logout/` - User logout
- `GET /api/auth/user/` - Get current user

#### IOU Endpoints
- `GET /api/ious/` - List all IOUs
- `POST /api/ious/` - Create new IOU
- `GET /api/ious/{id}/` - Get specific IOU
- `PUT/PATCH /api/ious/{id}/` - Update IOU
- `DELETE /api/ious/{id}/` - Delete IOU

#### Debt Endpoints
- `GET /api/debts/` - List all debts
- `POST /api/debts/` - Create new debt
- `GET /api/debts/{id}/` - Get specific debt
- `PUT/PATCH /api/debts/{id}/` - Update debt
- `DELETE /api/debts/{id}/` - Delete debt

#### Notification Endpoints
- `GET /api/notifications/` - List notifications
- `PATCH /api/notifications/{id}/` - Mark notification as read

## 📱 Application Structure

```
src/
├── assets/           # CSS and static assets
├── components/       # Reusable Vue components
│   └── layout/      # Layout components (Sidebar, TopNavbar, etc.)
├── router/          # Vue Router configuration
├── services/        # API service layer
├── stores/          # Pinia stores for state management
├── types/           # TypeScript type definitions
├── views/           # Page components
└── main.ts         # Application entry point
```

## 🎯 Key Features Explained

### Authentication
- Secure JWT-based authentication
- Protected routes that require login
- Automatic token refresh and logout on expiry
- User registration with validation

### IOU Management
- Create IOUs with debtor, creditor, amount, and due date
- Track who owes you money vs. who you owe
- Mark IOUs as paid or cancelled
- View detailed information and edit existing IOUs

### Dashboard
- Overview of total amounts owed to you and amounts you owe
- Recent IOU activity
- Upcoming due dates with overdue highlighting
- Quick statistics and summary cards

### Responsive Design
- Mobile-first design approach
- Collapsible sidebar navigation on mobile
- Touch-friendly interface elements
- Optimized for all screen sizes

## 🔧 Development

### Available Scripts

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Run type checking
npm run type-check

# Run linting
npm run lint

# Preview production build
npm run preview
```

### Project Configuration

The project uses several configuration files:

- `vite.config.ts` - Vite build configuration
- `tailwind.config.js` - Tailwind CSS configuration
- `tsconfig.json` - TypeScript configuration
- `postcss.config.js` - PostCSS configuration

### Code Style

- TypeScript for type safety
- Vue 3 Composition API
- Tailwind CSS for styling
- ESLint and Prettier for code formatting

## 🚀 Deployment

### Build for Production

```bash
npm run build
```

This creates a `dist/` directory with production-ready files.

### Deployment Options

The built application can be deployed to:

- **Netlify**: Drag and drop the `dist/` folder
- **Vercel**: Connect your GitHub repository
- **Firebase Hosting**: Use Firebase CLI
- **Traditional Web Server**: Upload `dist/` contents

### Environment Variables for Production

Set these environment variables in your deployment platform:

```env
VITE_API_BASE_URL=https://your-api-domain.com/api
```

## 📋 API Integration

### Authentication Flow

1. User logs in with username/password
2. Backend returns JWT token
3. Token stored in localStorage
4. Token sent in Authorization header for subsequent requests
5. Automatic logout if token expires

### Error Handling

The application includes comprehensive error handling:

- Network errors with user-friendly messages
- Form validation with field-specific errors
- API error responses displayed to users
- Loading states for better UX

## 🎨 UI/UX Features

### Design System
- Consistent color palette with primary, success, danger, and warning colors
- Standardized button styles and form components
- Responsive grid layouts
- Smooth transitions and hover effects

### Accessibility
- Semantic HTML structure
- Proper ARIA labels
- Keyboard navigation support
- Color contrast compliance

## 🐛 Troubleshooting

### Common Issues

1. **API Connection Failed**
   - Ensure Django backend is running on port 8000
   - Check CORS settings in Django
   - Verify API endpoints are accessible

2. **Build Errors**
   - Clear node_modules: `rm -rf node_modules && npm install`
   - Check Node.js version (18+ required)

3. **Styling Issues**
   - Ensure Tailwind CSS is properly configured
   - Check for conflicting CSS

### Development Tips

- Use Vue DevTools browser extension for debugging
- Check browser console for errors
- Use network tab to debug API calls
- Ensure backend API is running before starting frontend

## 📈 Performance

### Optimization Features
- Code splitting with Vue Router
- Lazy loading of route components
- Optimized bundle size with Vite
- Efficient state management with Pinia

### Best Practices
- Minimal re-renders with Vue's reactivity
- Efficient data fetching patterns
- Image optimization
- Gzip compression in production

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:

1. Check this README first
2. Look at the browser console for errors
3. Ensure the Django backend is properly configured
4. Check network requests in browser dev tools

## 🔮 Future Enhancements

Potential features for future development:

- Push notifications for payment reminders
- Export functionality (PDF, CSV)
- Multi-currency support
- Payment tracking and history
- Mobile app (React Native/Ionic)
- Email notifications
- Advanced reporting and analytics
