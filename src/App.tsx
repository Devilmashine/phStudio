import Navbar from './components/Navbar';
import Hero from './components/Hero';
import Studios from './components/Studios';
import BookingForm from './components/BookingForm';
import Footer from './components/Footer';

function App() {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-grow">
        <Hero />
        <Studios />
        <BookingForm />
      </main>
      <Footer />
    </div>
  );
}

export default App;