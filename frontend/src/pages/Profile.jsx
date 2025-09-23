import React, { useState, useEffect } from 'react';
import { profileAPI } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Loader2, Save, User, Instagram, Youtube, Music } from 'lucide-react';

const Profile = () => {
  const [profile, setProfile] = useState(null);
  const [formData, setFormData] = useState({
    display_name: '',
    bio: '',
    niche: '',
    social_links: {
      instagram: '',
      tiktok: '',
      youtube: '',
    },
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const nicheOptions = [
    { value: 'fashion', label: 'Moda' },
    { value: 'beauty', label: 'Beleza' },
    { value: 'fitness', label: 'Fitness' },
    { value: 'food', label: 'Comida' },
    { value: 'travel', label: 'Viagem' },
    { value: 'lifestyle', label: 'Lifestyle' },
    { value: 'tech', label: 'Tecnologia' },
    { value: 'gaming', label: 'Games' },
    { value: 'parenting', label: 'Maternidade/Paternidade' },
    { value: 'business', label: 'Negócios' },
    { value: 'other', label: 'Outro' },
  ];

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await profileAPI.getProfile();
        const profileData = response.data;
        setProfile(profileData);
        setFormData({
          display_name: profileData.display_name || '',
          bio: profileData.bio || '',
          niche: profileData.niche || '',
          social_links: {
            instagram: profileData.social_links?.instagram || '',
            tiktok: profileData.social_links?.tiktok || '',
            youtube: profileData.social_links?.youtube || '',
          },
        });
      } catch (err) {
        if (err.response?.status === 404) {
          // Profile doesn't exist yet, that's ok
          setProfile(null);
        } else {
          console.error('Error fetching profile:', err);
          setError('Erro ao carregar perfil');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    if (name.startsWith('social_')) {
      const socialField = name.replace('social_', '');
      setFormData({
        ...formData,
        social_links: {
          ...formData.social_links,
          [socialField]: value,
        },
      });
    } else {
      setFormData({
        ...formData,
        [name]: value,
      });
    }
  };

  const handleNicheChange = (value) => {
    setFormData({
      ...formData,
      niche: value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    setSuccess('');

    try {
      if (profile) {
        // Update existing profile
        await profileAPI.updateProfile(formData);
        setSuccess('Perfil atualizado com sucesso!');
      } else {
        // Create new profile
        const response = await profileAPI.createProfile(formData);
        setProfile(response.data);
        setSuccess('Perfil criado com sucesso!');
      }
    } catch (err) {
      console.error('Error saving profile:', err);
      setError(err.response?.data?.detail || 'Erro ao salvar perfil');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-foreground">Perfil</h1>
        <p className="text-muted-foreground">
          Gerencie suas informações pessoais e configurações
        </p>
      </div>

      {/* Profile Form */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <User className="h-5 w-5" />
            <span>Informações do Perfil</span>
          </CardTitle>
          <CardDescription>
            {profile ? 'Atualize suas informações' : 'Complete seu perfil para começar'}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            {success && (
              <Alert>
                <AlertDescription>{success}</AlertDescription>
              </Alert>
            )}

            <div className="space-y-2">
              <Label htmlFor="display_name">Nome de exibição</Label>
              <Input
                id="display_name"
                name="display_name"
                value={formData.display_name}
                onChange={handleChange}
                placeholder="Como você quer ser chamado"
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="bio">Bio</Label>
              <Textarea
                id="bio"
                name="bio"
                value={formData.bio}
                onChange={handleChange}
                placeholder="Conte um pouco sobre você e seu conteúdo"
                rows={3}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="niche">Nicho de atuação</Label>
              <Select value={formData.niche} onValueChange={handleNicheChange}>
                <SelectTrigger>
                  <SelectValue placeholder="Selecione seu nicho" />
                </SelectTrigger>
                <SelectContent>
                  {nicheOptions.map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Social Links */}
            <div className="space-y-4">
              <Label className="text-base font-semibold">Redes Sociais</Label>
              
              <div className="space-y-2">
                <Label htmlFor="social_instagram" className="flex items-center space-x-2">
                  <Instagram className="h-4 w-4" />
                  <span>Instagram</span>
                </Label>
                <Input
                  id="social_instagram"
                  name="social_instagram"
                  value={formData.social_links.instagram}
                  onChange={handleChange}
                  placeholder="https://instagram.com/seuusuario"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="social_tiktok" className="flex items-center space-x-2">
                  <Music className="h-4 w-4" />
                  <span>TikTok</span>
                </Label>
                <Input
                  id="social_tiktok"
                  name="social_tiktok"
                  value={formData.social_links.tiktok}
                  onChange={handleChange}
                  placeholder="https://tiktok.com/@seuusuario"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="social_youtube" className="flex items-center space-x-2">
                  <Youtube className="h-4 w-4" />
                  <span>YouTube</span>
                </Label>
                <Input
                  id="social_youtube"
                  name="social_youtube"
                  value={formData.social_links.youtube}
                  onChange={handleChange}
                  placeholder="https://youtube.com/@seucanal"
                />
              </div>
            </div>

            <Button type="submit" disabled={saving} className="w-full">
              {saving ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Salvando...
                </>
              ) : (
                <>
                  <Save className="mr-2 h-4 w-4" />
                  {profile ? 'Atualizar Perfil' : 'Criar Perfil'}
                </>
              )}
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Instagram Connection */}
      {profile && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Instagram className="h-5 w-5" />
              <span>Conexão com Instagram</span>
            </CardTitle>
            <CardDescription>
              Conecte sua conta do Instagram para análise automática
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between p-4 border border-border rounded-lg">
              <div>
                <p className="font-medium">Instagram Business API</p>
                <p className="text-sm text-muted-foreground">
                  {profile.instagram_tokens ? 'Conectado' : 'Não conectado'}
                </p>
              </div>
              <Button variant={profile.instagram_tokens ? 'outline' : 'default'}>
                {profile.instagram_tokens ? 'Reconectar' : 'Conectar'}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default Profile;

